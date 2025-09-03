from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
CORS(app)

# 数据库配置（不变）
try:
    db_port = int(os.getenv('MYSQL_PORT', 3306))
except ValueError:
    db_port = 3306

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql-db'),
    'port': db_port,
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '123456'),
    'database': os.getenv('MYSQL_DB', 'db_project_test')
}

def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("数据库连接成功！")
            return connection
    except Error as e:
        print(f"数据库连接错误: {str(e)}")
    return connection

# 接口1：各地区Top20游戏（严格匹配数据库字段名，解决未知问题）
@app.route('/api/sales/by-region-top20', methods=['GET'])
def get_region_top20():
    n = request.args.get('n', 20, type=int)
    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})

    try:
        cursor = connection.cursor(dictionary=True)
        # 查询所有字段（数据库字段是大写开头，如Rank、Platform）
        query = """
            SELECT * 
            FROM game_sales
            ORDER BY Global_Sales DESC
            LIMIT %s
        """
        cursor.execute(query, (n * 5,))
        games = cursor.fetchall()
        print(f"地区Top20查询到 {len(games)} 条数据（字段名匹配数据库）")

        # 数据预处理：严格使用数据库的大写开头字段名（关键修复！）
        processed_games = []
        for game in games:
            processed_games.append({
                # 数据库字段是Rank → 读取时用'Rank'
                'rank': game.get('Rank', 0),
                # 数据库字段是Name → 读取时用'Name'
                'name': game.get('Name', '未知游戏'),
                # 数据库字段是Platform → 读取时用'Platform'（解决“未知平台”）
                'platform': game.get('Platform', '未知平台'),
                # 数据库字段是Year → 读取时用'Year'
                'year': game.get('Year', '未知年份'),
                # 数据库字段是Genre → 读取时用'Genre'
                'genre': game.get('Genre', '未知类型'),
                # 数据库字段是Publisher → 读取时用'Publisher'（解决“未知发行商”）
                'publisher': game.get('Publisher', '未知发行商'),
                # 销量字段：数据库是NA_Sales、EU_Sales等（大写开头）
                'na_sales': float(game.get('NA_Sales', 0)) if game.get('NA_Sales') is not None else 0.0,
                'eu_sales': float(game.get('EU_Sales', 0)) if game.get('EU_Sales') is not None else 0.0,
                'jp_sales': float(game.get('JP_Sales', 0)) if game.get('JP_Sales') is not None else 0.0,
                'other_sales': float(game.get('Other_Sales', 0)) if game.get('Other_Sales') is not None else 0.0,
                'global_sales': float(game.get('Global_Sales', 0)) if game.get('Global_Sales') is not None else 0.0
            })

        # 调试：打印第一条数据，确认平台和发行商是否正确
        if processed_games:
            print("第一条游戏数据（修复后）：", {
                'name': processed_games[0]['name'],
                'platform': processed_games[0]['platform'],
                'publisher': processed_games[0]['publisher']
            })

        return jsonify({'code': 200, 'msg': 'success', 'data': processed_games})

    except Error as e:
        error_msg = f"地区Top20查询错误: {str(e)}"
        print(error_msg)
        return jsonify({'code': 500, 'msg': error_msg, 'data': []})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 接口2：各类型最畅销游戏（已正常，保持不变）
@app.route('/api/sales/by-genre-top', methods=['GET'])
def get_genre_top():
    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                g.genre,
                g.name as top_game_name,
                g.global_sales as sales
            FROM game_sales g
            INNER JOIN (
                SELECT genre, MAX(global_sales) as max_sales
                FROM game_sales
                WHERE genre IS NOT NULL AND genre != ''
                GROUP BY genre
            ) sub ON g.genre = sub.genre AND g.global_sales = sub.max_sales
            ORDER BY g.global_sales ASC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        print(f"类型畅销榜查询到 {len(result)} 条数据")

        for item in result:
            item['sales'] = float(item['sales']) if item['sales'] is not None else 0.0

        return jsonify({'code': 200, 'msg': 'success', 'data': result})

    except Error as e:
        error_msg = f"类型畅销榜查询错误: {str(e)}"
        print(error_msg)
        return jsonify({'code': 500, 'msg': error_msg, 'data': []})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 接口3.1：筛选器元数据（微调：与数据库字段名大小写一致）
@app.route('/api/filters/meta', methods=['GET'])
def get_filter_meta():
    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': {}})

    try:
        cursor = connection.cursor()
        meta_data = {'genres': [], 'platforms': [], 'publishers': []}

        # 关键：查询字段名改为大写开头（与数据库一致：Genre/Platform/Publisher）
        cursor.execute("SELECT DISTINCT Genre FROM game_sales WHERE Genre IS NOT NULL AND Genre != '' ORDER BY Genre")
        meta_data['genres'] = [row[0] for row in cursor.fetchall()] or []
        cursor.execute("SELECT DISTINCT Platform FROM game_sales WHERE Platform IS NOT NULL AND Platform != '' ORDER BY Platform")
        meta_data['platforms'] = [row[0] for row in cursor.fetchall()] or []
        cursor.execute("SELECT DISTINCT Publisher FROM game_sales WHERE Publisher IS NOT NULL AND Publisher != '' ORDER BY Publisher")
        meta_data['publishers'] = [row[0] for row in cursor.fetchall()] or []

        print(f"筛选器元数据：类型{len(meta_data['genres'])}个，平台{len(meta_data['platforms'])}个，发行商{len(meta_data['publishers'])}个")
        return jsonify({'code': 200, 'msg': 'success',** meta_data})

    except Error as e:
        error_msg = f"筛选器元数据查询错误: {str(e)}"
        print(error_msg)
        return jsonify({'code': 500, 'msg': error_msg, 'data': {}})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/api/games/filtered', methods=['GET'])
def get_filtered_games():
    # 处理参数：只去首尾空格
    genre = request.args.get('genre', '').strip()
    platform = request.args.get('platform', '').strip()
    publisher = request.args.get('publisher', '').strip()

    print(f"\n【筛选参数】genre='{genre}', platform='{platform}', publisher='{publisher}'")

    if not all([genre, platform, publisher]):
        return jsonify({'code': 400, 'msg': '请选择完整的筛选条件（类型/平台/发行商）', 'data': []})

    connection = create_db_connection()
    if not connection:
        return jsonify({'code': 500, 'msg': '数据库连接失败', 'data': []})

    try:
        cursor = connection.cursor(dictionary=True)
        # 关键修复：用反引号包裹保留字`Rank`
        query = (
            "SELECT `Rank`, Name, Platform, Publisher, Genre, Global_Sales "
            "FROM game_sales "
            "WHERE LOWER(TRIM(Genre)) = LOWER(%s) "
            "AND LOWER(TRIM(Platform)) = LOWER(%s) "
            "AND LOWER(TRIM(Publisher)) = LOWER(%s) "
            "ORDER BY Global_Sales DESC"
        )
        
        cursor.execute(query, (genre, platform, publisher))
        games = cursor.fetchall()
        print(f"【执行SQL】{cursor.statement}")
        print(f"【筛选结果】查询到 {len(games)} 条数据")

        # 数据格式化（兼容大小写字段名）
        result = []
        for game in games:
            result.append({
                'Rank': game.get('Rank', game.get('rank', 0)),
                'Name': game.get('Name', game.get('name', '未知游戏')),
                'Platform': game.get('Platform', game.get('platform', '未知平台')),
                'Publisher': game.get('Publisher', game.get('publisher', '未知发行商')),
                'Genre': game.get('Genre', game.get('genre', '未知类型')),
                'Global_Sales': float(game.get('Global_Sales', game.get('global_sales', 0))) 
                                if (game.get('Global_Sales') or game.get('global_sales')) else 0.0
            })

        return jsonify({'code': 200, 'msg': 'success', 'data': result})

    except Error as e:
        error_msg = f"筛选查询错误: SQL={cursor.statement if 'cursor' in locals() else '未生成'}, 错误={str(e)}"
        print(f"【筛选错误】{error_msg}")
        return jsonify({'code': 500, 'msg': error_msg, 'data': []})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    


if __name__ == '__main__':
    print("后端服务启动中...")
    print(f"监听地址：http://0.0.0.0:5000")
    print(f"数据库配置：{DB_CONFIG}")
    app.run(host='0.0.0.0', port=5000, debug=True)
    