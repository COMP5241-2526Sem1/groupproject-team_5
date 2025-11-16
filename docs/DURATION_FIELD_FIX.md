# 活动时长字段修复说明

## 问题描述
在老师创建活动页面，既出现了可以自行设计时分秒的输入框，又出现了原来的分钟下拉选择框。两个UI组件同时显示，导致自行设计的时分秒输入框不能正常工作。

## 问题原因
在 `app/forms.py` 文件中，`ActivityForm` 的 `duration_minutes` 字段被定义为 `SelectField`（下拉选择框）：

```python
duration_minutes = SelectField('Activity Duration', 
    choices=[(1, '1 minute'), (3, '3 minutes'), (5, '5 minutes'), 
             (10, '10 minutes'), (15, '15 minutes'), (30, '30 minutes')], 
    coerce=int, default=5)
```

这会在页面上渲染出一个旧的分钟选择下拉框。

而在 `templates/activities/create_activity.html` 中，又添加了新的时分秒自定义输入框组件，导致两个组件同时显示。

## 解决方案
将 `duration_minutes` 字段从 `SelectField` 改为 `HiddenField`，这样：
1. 不会显示旧的下拉选择框
2. 仍然保留该字段用于表单提交
3. JavaScript代码会在提交前计算时分秒的总分钟数并填充到这个隐藏字段中

## 修改内容

### 文件：`app/forms.py`

**修改前：**
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, SubmitField, RadioField
```

**修改后：**
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FileField, SubmitField, RadioField, HiddenField
```

**修改前：**
```python
class ActivityForm(FlaskForm):
    title = StringField('Activity Title', validators=[DataRequired(), Length(min=2, max=200)])
    type = SelectField('Activity Type', choices=[('poll', 'Poll'), ('short_answer', 'Short Answer'), ('quiz', 'Quiz'), ('word_cloud', 'Word Cloud'), ('memory_game', 'Memory Game')], validators=[DataRequired()])
    question = TextAreaField('Question', validators=[DataRequired()])
    options = TextAreaField('Options (Required for polls, one per line)')
    duration_minutes = SelectField('Activity Duration', choices=[(1, '1 minute'), (3, '3 minutes'), (5, '5 minutes'), (10, '10 minutes'), (15, '15 minutes'), (30, '30 minutes')], coerce=int, default=5)
    submit = SubmitField('Create Activity')
```

**修改后：**
```python
class ActivityForm(FlaskForm):
    title = StringField('Activity Title', validators=[DataRequired(), Length(min=2, max=200)])
    type = SelectField('Activity Type', choices=[('poll', 'Poll'), ('short_answer', 'Short Answer'), ('quiz', 'Quiz'), ('word_cloud', 'Word Cloud'), ('memory_game', 'Memory Game')], validators=[DataRequired()])
    question = TextAreaField('Question', validators=[DataRequired()])
    options = TextAreaField('Options (Required for polls, one per line)')
    duration_minutes = HiddenField('Activity Duration', default=5)
    submit = SubmitField('Create Activity')
```

## 工作原理
1. 用户在页面上看到时、分、秒三个输入框（可手动输入或通过下拉菜单选择）
2. 用户输入完成后提交表单
3. JavaScript在表单提交时拦截，计算总秒数：`totalSeconds = hours * 3600 + minutes * 60 + seconds`
4. 将总秒数转换为分钟数（向上取整）：`totalMinutes = Math.ceil(totalSeconds / 60)`
5. 将计算结果填充到隐藏的 `duration_minutes` 字段中
6. 表单正常提交，后端接收到的是计算后的总分钟数

## 测试建议
1. 打开创建活动页面，确认不再显示旧的分钟下拉选择框
2. 只显示时、分、秒三个输入框
3. 测试设置1小时（60分钟），确认活动创建成功且时长正确
4. 测试设置混合时长（如1小时30分钟45秒），确认计算正确

## 修改日期
2025年11月11日

## 分支
zmd分支
