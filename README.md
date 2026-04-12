# project 3
## 问题（Problem）
引入引导导航（通过结构化步骤和方向提示）相比无引导界面，是否能提升用户任务的完成度和效率？

**English:**
Does introducing guided navigation (through structured steps and directional cues) improve user task completion and efficiency compared to an unguided interface?

---

## Version A（无引导）
特点：
- 页面信息比较平铺

---

## Version B（有引导）
特点：
- 明确的任务流程

---

## 评估指标（Metrics）

### 1. Task Completion Rate
定义：用户是否成功完成指定任务  
例如：
- 上传一个数据集  
- 进入 EDA 页面并成功生成一个图表  

---

### 2. Time to Completion
定义：从进入 app 到完成任务所花费的时间  

---

### 3. Upload Success Rate
定义：成功上传文件的用户占比  

---

### 4. Visualization Generation Rate
定义：成功生成图表的用户占比  

---

### 5. Bounce / Exit Rate
定义：用户是否在完成任务前退出  

---

### 6. Number of Clicks / Interactions
定义：完成任务前的点击次数  

---

## 实验流程（Experiment Design）

### Step 1: 随机分组
用户进入 app 时，随机分配到 A 或 B  

- 50% → Version A  
- 50% → Version B  

---

### Step 2: 统一任务
给所有用户同一个任务，例如：

> Please upload a dataset and create one visualization using the app.

---

### Step 3: 行为日志记录
记录以下信息：

- user_id（或 IP）
- group（A / B）
- entry time
- upload clicked
- upload success
- summary viewed
- visualization created
- completion status
- completion time

---

### Step 4: A/B 差异分析
对比 Version A 和 Version B 在各项指标上的表现差异

---

## 使用指南
由于这两个版本还没正式确定，没有部署。

---

### Step 1: 准备三个terminal
第一个terminal:
```{bash}
shiny run --host 127.0.0.1 --port 8001 app_A.py
```
第二个terminal：
```{bash}
shiny run --host 127.0.0.1 --port 8002 app_B.py
```
执行完前面两个之后，在第三个terminal执行：
```{bash}
uvicorn app_entry:app --reload --host 127.0.0.1 --port 8000
```
然后打开：
```{bash}
http://127.0.0.1:8000/
```

后续确定好两个版本并部署后使用起来会简单点
