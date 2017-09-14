# 全品类标签提取

### 流程
##### 1) 获取某个品类的评论文本

##### 2) 基于评论文本提取特征词/评价词

特征词/评价词库的作用：
- 分词
- 归一化

```python
pinglun_file = os.path.join(RESOURCE_DIR, 'mobile.sample')
O_seeds = {u'不错', u'漂亮', u'流畅', u'方便', u'高', u'持久'}
feature_clusters, opinions = lexicon_extractor.extract(pinglun_file, O_seeds)
```
##### 3) 人工修正/整理评价词库

##### 4) 提取标签

- 提取一段文本的标签
```
txt = u'手机屏幕漂亮的很，大小也合适。'
labels = labeler.extract_from_txt(txt)
for label in labels:
    print label
```

- 从一个文件里提取标签
```
labels = labeler.extract_from_file(os.path.join(RESOURCE_DIR, 'clean', 'mobile.sample.min.clean'))
for label in labels:
    print label
```