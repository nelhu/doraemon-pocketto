# Skills

本目录用于存放可复用的 AI 工作流、操作规范及其配套资源。

## 组织方式

每个 skill 使用独立目录，目录名使用简短、可辨识的 kebab-case：

```text
skills/
└── example-skill/
    ├── SKILL.md
    ├── scripts/       # 可选：辅助脚本
    ├── references/    # 可选：参考资料
    └── assets/        # 可选：skill 专属素材
```

`SKILL.md` 至少应说明适用场景、输入、执行流程、输出和依赖。只添加当前确实需要的文件，避免复制无关模板。

## 安全

- 不提交账号、密钥、Token、Cookie 等敏感信息。
- 脚本执行前说明其副作用和所需权限。
- 引用外部 skill 时记录来源、版本和许可证。
