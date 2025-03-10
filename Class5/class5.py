# 運算子
print(1 + 1)  # 加法
print(3 - 2)  # 減法
print(4 * 5)  # 乘法
print(6 / 2)  # 除法
print(7 // 2)  # 整除
print(8 % 2)  # 取餘數
print(9**10)  # 指數

# 優先順序
# 1.()括號
# 2.**次方
# 3.* / // %乘除取商取餘數
# 4.+ - 加減

# input() 讓使用者在終端機輸入資料
# input() 的括弧內可以放入"提示字串"
a = input("請輸入正方形邊長：")
# 透過 input() 輸入的資料都是字串
print(a + "1")  # 字串相加

# 正方形面積計算
r = input("請輸入正方形邊長：")
r = int(r)  # 將字串轉換整數
area = r * r  # 計算面積
print(f"正方形面積為：{area}")  # 印出面積
