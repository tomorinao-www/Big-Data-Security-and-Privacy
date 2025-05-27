from scipy.spatial import KDTree


# ====== 加载二维数据 ======
def load_data(filename) -> list[tuple[float, float]]:
    """从文件加载二维数据"""
    data = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                x, y = float(parts[0]), float(parts[1])
                data.append((x, y))
    return data


# ====== 保序加密函数（简化线性OPE） ======
def ope_encrypt(value, key, slope=1000) -> float:
    return slope * value + key


# ====== 对每个维度独立加密 ======
def encrypt_dataset(data, key_x, key_y, slope=1000) -> list[tuple[float, float]]:
    encrypted = []
    for x, y in data:
        enc_x = ope_encrypt(x, key_x, slope)
        enc_y = ope_encrypt(y, key_y, slope)
        encrypted.append((enc_x, enc_y))
    return encrypted


# ====== 查询最近邻点 ======
def query_nearest(tree: KDTree, query_point, k, key_x, key_y, slope=1000) -> list:
    qx, qy = query_point
    enc_qx = ope_encrypt(qx, key_x, slope)
    enc_qy = ope_encrypt(qy, key_y, slope)
    print(f"加密后的查询点坐标: ({enc_qx}, {enc_qy})")
    distances, indices = tree.query((enc_qx, enc_qy), k=k)
    if k == 1:
        indices = [indices]
    return indices


# ====== 主程序入口 ======
def main():
    # 参数设置
    filename = "NE.txt"
    key_x, key_y = 314, 628  # 加密密钥
    slope = 1000  # 加密斜率，保持顺序结构

    # 加载并加密数据
    raw_data = load_data(filename)
    encrypted_data = encrypt_dataset(raw_data, key_x, key_y, slope)

    # 构建KD树索引
    tree = KDTree(encrypted_data)

    # 用户输入查询点
    print("请输入查询点坐标 (格式：x y)，例如：0.36 0.40")
    qx, qy = map(float, input("Query: ").split())
    k = int(input("返回前k个近邻，k = "))

    # 执行查询
    indices = query_nearest(tree, (qx, qy), k, key_x, key_y, slope)

    # 输出结果
    print(f"\n最近邻查询结果（k = {k}）：")
    for idx in indices:
        print(f"Index {idx}:  密文:{encrypted_data[idx]}  明文:{raw_data[idx]}")


if __name__ == "__main__":
    main()
