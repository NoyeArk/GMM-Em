import csv
import random
import numpy as np
from scipy.stats import multivariate_normal


def read_data(filename):
    print('数据集路径为：', filename)

    x = []  # 存储读取到的数据
    with open(filename, 'r') as file:
        print(1)
        csv_reader = csv.reader(file, delimiter=' ')
        print(2)
        for row in csv_reader:
            print(3)
            # 将每一行数据转换为浮点数列表
            row_data = [float(val) for val in row]
            x.append(row_data)

    return np.array(x)


class GMM:
    def __init__(self, n_components, iter=1000, eps=1e-10):
        print('GMM1111')

        self.n_components, self.iter, self.eps = n_components, iter, eps
        self.weights = np.full(self.n_components, 1 / self.n_components)
        self.last_weights = self.weights
        self.means, self.cov = None, None

    def fit(self, x):
        self.means = np.array(x[random.sample(range(x.shape[0]), self.n_components)])

        self.cov = np.stack([np.eye(x.shape[1]) for _ in range(self.n_components)])
        last_loss = -float('inf')

        for _ in range(self.iter):
            pi = self.e_step(x)  # E步
            self.m_step(x, pi)  # M步
            # 判断分概率分布是否变化不大
            cur_loss = np.sum(np.log(np.dot(self.weights, self.last_weights.T)), axis=0)
            if abs(cur_loss - last_loss) < self.eps:
                break
            last_loss = cur_loss

    def pred(self, x):
        pi = self.e_step(x)
        return np.argmax(pi, axis=1)

    def e_step(self, x):  # E步
        n_samples = x.shape[0]
        n_components = self.means.shape[0]

        # 计算每个样本属于各个高斯分量的概率
        probs = np.zeros((n_samples, n_components))
        for k in range(n_components):
            dist = multivariate_normal(mean=self.means[k], cov=self.cov[k])
            probs[:, k] = self.weights[k] * dist.pdf(x)

        # 归一化每个样本的概率
        probs /= np.sum(probs, axis=1, keepdims=True)
        return probs

    def m_step(self, x, pi):  # M步
        self.last_weights = self.weights

        # 更新均值和协方差
        N = pi.sum(axis=0)
        self.means = (pi.T @ x) / np.expand_dims(N, axis=1)
        self.cov = np.zeros_like(self.cov)
        for k in range(self.n_components):
            x_pro = x - self.means[k]
            self.cov[k] = (np.expand_dims(pi[:, k], axis=0) * x_pro.T @ x_pro) / pi[:, k].sum()

        # 更新权重
        self.weights = pi.mean(axis=0)

        # 添加微小协方差防止奇异
        self.cov += 1e-6 * np.eye(x.shape[1])




if __name__ == "__main__":
    gmm = GMM(6)

    gmm.x = read_data()