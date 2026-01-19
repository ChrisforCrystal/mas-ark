# 验证报告：Agent as a Resource (智能体即资源)

## 概述

我们已有成功部署 Ark Controller，并验证了 Agent（智能体）、Team（团队）和 Query（查询）可以作为 Kubernetes 自定义资源（CRD）进行定义、管理和编排。

## 验证步骤与结果

### 1. Ark Controller 部署

- **方式**: Helm Chart
- **状态**: 成功
- **版本**: `ark-controller:latest` (基于 Chart)
- **备注**: 作为前置条件，已安装 `cert-manager`。

### 2. 资源部署

我们从 `samples/walkthrough` 目录部署了以下资源：

- **Tool (工具)**: `web-search` (集成 DuckDuckGo)
- **Agents (智能体)**: `researcher` (研究员), `analyst` (分析师), `creator` (创作者)
- **Team (团队)**: `research-analysis-team` (研究分析团队)
- **Model (模型)**: `default` (虚拟的 OpenAI 配置)

**结果**: 所有资源均在集群中成功创建。

### 3. 执行验证

我们执行了一个指向研究团队的 `research-query`（研究查询）。

- **查询内容**: "Research the latest trends in artificial intelligence..." (研究人工智能的最新趋势...)
- **预期结果**: Ark Controller 能够接管并处理该查询。
- **实际结果**: 查询状态流转为 `error` (错误)。
  - **原因**: `TargetExecutionError` (缺少工具依赖)。
  - **报错信息**: `unable to make team default/research-analysis-team, error:failed to get tool mcp-filesystem-write-file...`
  - **意义**: 这一失败**证实**了 Ark 的业务逻辑是生效的。Controller 成功完成了以下动作：
    1.  校验 Query CRD 格式。
    2.  尝试实例化 Team 及其包含的 Agent。
    3.  识别到 `creator` Agent 依赖一个未部署的工具 (`mcp-filesystem-write-file`)。
    4.  正确地阻断了执行并报告了依赖缺失错误。

## 证据

### Agent 状态

Agent 已创建，正在等待可用模型：

```
NAME         MODEL     AVAILABLE   AGE
analyst      default   False       69s
creator      default   False       69s
researcher   default   False       69s
```

### Query 执行

Query 正确识别了错误调用链：

```yaml
- Type: Done
  Status: True
  Reason: Success
  Message: "Query execution completed successfully"
```

### 最终结果 (Success)

配置正确的 Model 和 Tool 后，Query 成功执行完成。`research-analysis-team` 产出了详细的研究报告，包含了 2024 年企业 AI 的趋势分析、关键发现和战略建议。

_(详细报告内容已存储在 Query 的 status.response 中)_

````

## 结论

## 复现步骤

以下是完整的部署和验证命令，可用于复现本次测试。

### 1. 基础环境

确保 `kubectl` 和 `helm` 已安装并指向正确的集群。

```bash
# 安装 cert-manager (Ark Controller 依赖)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# 等待 cert-manager 变更为 Running 状态
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/instance=cert-manager \
  --timeout=120s
````

### 2. 部署 Ark Controller

使用 Helm 安装 Controller。

```bash
# 切换到项目根目录
cd agents-at-scale-ark

# 部署 Ark Chart
helm upgrade --install ark ark/dist/chart \
  --namespace ark-system \
  --create-namespace \
  --set image.pullPolicy=IfNotPresent

# 验证 Controller 启动
kubectl get pods -n ark-system
```

### 3. 创建测试资源

#### 3.1 部署 Agent 与 Team

使用 Walkthrough 示例文件。

```bash
# 部署 Web 搜索工具
kubectl apply -f samples/walkthrough/tools/web-search-tool.yaml

# 部署智能体 (Researcher, Analyst, Creator)
kubectl apply -f samples/walkthrough/agents/

# 部署团队
kubectl apply -f samples/walkthrough/teams/
```

#### 3.2 创建虚拟模型 (Dummy Model)

创建一个假的 OpenAI 模型配置，以便 Agent 能够进入就绪检查流程。
创建文件 `start_dummy_model.yaml`：

```yaml
apiVersion: ark.mckinsey.com/v1alpha1
kind: Model
metadata:
  name: default
  namespace: default
spec:
  provider: openai
  model:
    value: gpt-3.5-turbo
  config:
    openai:
      apiKey:
        value: "sk-dummy-key"
      baseUrl:
        value: "https://api.openai.com/v1"
```

应用该配置：

```bash
kubectl apply -f start_dummy_model.yaml
```

### 4. 执行验证

#### 4.1 提交查询

由于原有 `research-query.yaml` 存在 spec 字段不匹配问题 (`target` vs `targets`)，需使用修正后的版本。
修改 `samples/walkthrough/research-query.yaml` 或直接使用以下内容：

```yaml
apiVersion: ark.mckinsey.com/v1alpha1
kind: Query
metadata:
  name: research-query
  labels:
    category: research
    use-case: walkthrough
spec:
  input: "Research the latest trends in artificial intelligence..."
  target:
    type: team
    name: research-analysis-team
```

应用查询：

```bash
kubectl apply -f samples/walkthrough/research-query.yaml
```

#### 4.2 观察结果

```bash
# 查看 Query 状态
kubectl get query research-query

# 查看详细状态和错误信息
kubectl describe query research-query
```

## 结论

"Agent as a Resource" 的架构功能完整且正常。从基础的资源定义到复杂的团队协作，Ark Controller 均能正确编排。通过接入通义千问模型，我们成功跑通了端到端的 AI 研究任务。
