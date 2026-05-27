# Introduction to Machine Learning

## What is Machine Learning?

Machine learning (ML) is a subset of artificial intelligence where systems learn patterns from data instead of being explicitly programmed for every rule. The goal is to build models that generalize: they perform well on new, unseen examples.

## Types of Learning

### Supervised Learning
The algorithm learns from labeled examples. Each training sample has an input **X** and a target **y**. Common tasks:
- **Classification**: predict a category (spam vs. not spam)
- **Regression**: predict a continuous value (house price)

### Unsupervised Learning
Only inputs are provided; the model finds structure in data. Examples include clustering (grouping customers) and dimensionality reduction (compressing features while preserving information).

### Reinforcement Learning
An agent takes actions in an environment and receives rewards or penalties. It learns a policy that maximizes cumulative reward over time.

## Train / Validation / Test Split

To estimate real-world performance, data is split:
1. **Training set** (~60–70%): fit model parameters
2. **Validation set** (~15–20%): tune hyperparameters and compare models
3. **Test set** (~15–20%): final unbiased evaluation — use only once at the end

Never tune on the test set; that causes **data leakage** and overly optimistic metrics.

## Overfitting and Underfitting

- **Underfitting**: model is too simple; high error on training and test data
- **Overfitting**: model memorizes training noise; low training error but poor test performance

Mitigations include more data, regularization (L1/L2), dropout (neural nets), simpler models, and cross-validation.

## Key Metrics

| Task | Common metrics |
|------|----------------|
| Classification | Accuracy, precision, recall, F1, ROC-AUC |
| Regression | MAE, MSE, RMSE, R² |

Choose metrics aligned with business cost (e.g., false negatives in medical screening may be worse than false positives).

## Gradient Descent (Intuition)

Many models minimize a **loss function** by iteratively updating parameters in the direction that reduces loss. Learning rate controls step size: too large → unstable; too small → slow convergence.
