import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


# 指定字体为 SimHei（黑体）
plt.rcParams["font.family"] = "SimHei"
# 避免坐标轴负号显示异常
plt.rcParams["axes.unicode_minus"] = False


# ========== 数据加载 ==========
def load_adult_data(filepath="adult.data.txt") -> pd.DataFrame:
    df = pd.read_csv(filepath, header=None, na_values="?", skipinitialspace=True)
    df.columns = [
        "age",
        "workclass",
        "fnlwgt",
        "education",
        "education-num",
        "marital-status",
        "occupation",
        "relationship",
        "race",
        "sex",
        "capital-gain",
        "capital-loss",
        "hours-per-week",
        "native-country",
        "income",
    ]
    df.dropna(inplace=True)

    return df


# ========== k匿名处理（基于年龄分桶） ==========
def k_anonymize(df, k=5):
    df["age_bucket"] = (df["age"] // k) * k + k / 2  # 每k岁一个桶


# ========== 差分隐私处理（拉普拉斯机制） ==========
def dp_age_mean(df, epsilon):
    sensitivity = (df["age"].max() - df["age"].min()) / len(df)
    noise = np.random.laplace(0, sensitivity / epsilon)
    return df["age"].mean() + noise  # 返回添加噪声后的平均年龄


# ========== 删除一条记录的敏感性分析 ==========
def leave_one_out_analysis(df, epsilon) -> tuple[list, list, list]:
    true_avg_list = []
    k_avg_list = []
    dp_avg_list = []

    for i in range(len(df)):
        df_dropped = df.drop(index=i)
        true_avg = df_dropped["age"].mean()
        k_anonymize(df_dropped)
        k_avg = df_dropped["age_bucket"].mean()
        dp_avg = dp_age_mean(df_dropped, epsilon=epsilon)
        true_avg_list.append(true_avg)
        k_avg_list.append(k_avg)
        dp_avg_list.append(dp_avg)

    return true_avg_list, k_avg_list, dp_avg_list


# ========== 主程序 ==========
def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    filepath = "adult.data.txt"
    if not os.path.exists(filepath):
        print(f"找不到数据文件：{filepath}")
        return

    df = load_adult_data(filepath)
    true_avg = df["age"].mean()

    # k-匿名处理
    k = int(input("请输入进行k匿名处理的k值："))
    k_anonymize(df, k)
    k_avg = df["age_bucket"].mean()

    # 差分隐私处理
    epsilon = 3.0

    dp_avg = dp_age_mean(df, epsilon)

    print("=== 平均年龄发布比较 ===")
    print(f"真实平均年龄: {true_avg:.6f}")
    print(f"k匿名平均年龄: {k_avg:.6f}")
    print(f"差分隐私平均年龄: {dp_avg:.6f}")

    # 可视化结果
    plt.figure(figsize=(10, 6))
    plt.hist(df["age"], bins=20, alpha=0.5, label="真实年龄")
    plt.hist(df["age_bucket"], bins=20, alpha=0.5, label="k-匿名年龄")
    plt.title("年龄分布与隐私保护策略对比")
    plt.xlabel("年龄")
    plt.ylabel("人数")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("age_privacy_comparison.png")
    plt.show()

    # 敏感性分析（只用前100条）
    print("\n正在进行敏感性分析（使用前100条数据）...")
    df_small = df.head(100).reset_index(drop=True)

    true_avg_list, k_avg_list, dp_avg_list = leave_one_out_analysis(df_small, epsilon)
    plt.figure(figsize=(10, 5))
    plt.plot(true_avg_list, label="真实平均", color="red", marker="o")
    plt.plot(k_avg_list, label="k匿名平均", color="blue", linestyle="--", alpha=0.6)
    plt.plot(dp_avg_list, label="差分隐私平均", color="orange", alpha=0.7)

    plt.title("删除单条记录后的平均年龄变化")
    plt.xlabel("被删除记录编号")
    plt.ylabel("平均年龄")
    plt.legend()
    plt.tight_layout()
    plt.savefig("sensitivity_analysis.png")
    plt.show()


if __name__ == "__main__":
    main()
