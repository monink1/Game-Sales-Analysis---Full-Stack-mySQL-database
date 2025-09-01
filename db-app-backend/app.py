from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func  # 导入聚合函数

app = Flask(__name__)
# 数据库配置（与docker-compose.yml一致）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@mysql-db:3306/db_project_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # 解决跨域

# 游戏销量模型（匹配数据库表结构）
class GameSales(db.Model):
    __tablename__ = 'game_sales'
    Rank = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255))
    Platform = db.Column(db.String(50))
    Year = db.Column(db.Integer)
    Genre = db.Column(db.String(50))
    Publisher = db.Column(db.String(100))
    NA_Sales = db.Column(db.Float)
    EU_Sales = db.Column(db.Float)
    JP_Sales = db.Column(db.Float)
    Other_Sales = db.Column(db.Float)
    Global_Sales = db.Column(db.Float)

# 接口1：全球销量Top10
@app.route('/api/sales/top', methods=['GET'])
def get_top_sales():
    top_n = request.args.get('n', 10, type=int)
    top_games = GameSales.query.order_by(GameSales.Global_Sales.desc()).limit(top_n).all()
    result = [{
        'Rank': game.Rank,
        'Name': game.Name,
        'Platform': game.Platform,
        'Global_Sales': float(game.Global_Sales)
    } for game in top_games]
    return jsonify({'code': 200, 'data': result, 'msg': 'success'})

# 接口2：按平台统计总销量（柱状图用）
@app.route('/api/sales/by-platform', methods=['GET'])
def sales_by_platform():
    platform_data = db.session.query(
        GameSales.Platform,
        func.sum(GameSales.Global_Sales).label('total_sales')
    ).group_by(GameSales.Platform).order_by(func.sum(GameSales.Global_Sales).desc()).all()
    result = {
        'platforms': [item.Platform for item in platform_data],
        'total_sales': [float(item.total_sales) for item in platform_data]
    }
    return jsonify({'code': 200, 'data': result, 'msg': 'success'})

# 接口3：按地区统计销量（饼图用）
@app.route('/api/sales/by-region', methods=['GET'])
def sales_by_region():
    # 统计北美、欧洲、日本、其他地区总销量
    region_data = db.session.query(
        func.sum(GameSales.NA_Sales).label('NA'),
        func.sum(GameSales.EU_Sales).label('EU'),
        func.sum(GameSales.JP_Sales).label('JP'),
        func.sum(GameSales.Other_Sales).label('Other')
    ).first()
    # 格式化为前端饼图需要的结构
    regions = ['北美', '欧洲', '日本', '其他']
    sales = [
        float(region_data.NA) if region_data.NA else 0,
        float(region_data.EU) if region_data.EU else 0,
        float(region_data.JP) if region_data.JP else 0,
        float(region_data.Other) if region_data.Other else 0
    ]
    result = [{'region': r, 'sales': s} for r, s in zip(regions, sales)]
    return jsonify({'code': 200, 'data': result, 'msg': 'success'})

# 接口4：PC端游戏销量排行Top20
@app.route('/api/sales/pc-top20', methods=['GET'])
def pc_top20():
    # 筛选平台为PC的游戏，按全球销量降序取前20
    pc_games = GameSales.query.filter(
        GameSales.Platform == 'PC'
    ).order_by(GameSales.Global_Sales.desc()).limit(20).all()
    
    result = [{
        'Rank': game.Rank,
        'Name': game.Name,
        'Publisher': game.Publisher,
        'Global_Sales': float(game.Global_Sales)
    } for game in pc_games]
    return jsonify({'code': 200, 'data': result, 'msg': 'success'})

# 接口5：前十畅销发行商的Top3游戏
@app.route('/api/sales/top-publishers', methods=['GET'])
def top_publishers():
    # 步骤1：获取销量最高的前十发行商（按总销量排序）
    top_publishers = db.session.query(
        GameSales.Publisher,
        func.sum(GameSales.Global_Sales).label('total_sales')
    ).group_by(GameSales.Publisher).order_by(func.sum(GameSales.Global_Sales).desc()).limit(10).all()
    
    # 步骤2：对每个发行商，查询其销量最高的3款游戏
    result = []
    for publisher, total_sales in top_publishers:
        # 查询该发行商的Top3游戏
        top_games = GameSales.query.filter(
            GameSales.Publisher == publisher
        ).order_by(GameSales.Global_Sales.desc()).limit(3).all()
        
        # 格式化数据（包含发行商总销量和旗下Top3游戏）
        result.append({
            'publisher': publisher,
            'total_sales': float(total_sales),
            'top_games': [{
                'name': game.Name,
                'sales': float(game.Global_Sales),
                'platform': game.Platform
            } for game in top_games]
        })
    
    return jsonify({'code': 200, 'data': result, 'msg': 'success'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)