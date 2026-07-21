# MCPs

本目录用于管理 MCP Server 的接入文档、配置示例和辅助脚本。

## 组织方式

每个 MCP Server 使用独立目录：

```text
mcps/
└── example-server/
    ├── README.md
    ├── config.example.json
    └── scripts/               # 可选：启动或验证脚本
```

README 应说明 Server 能力、运行方式、所需环境变量、客户端配置、可用工具和最小验证方法。

## 安全

- 配置示例使用占位符，不提交真实 Token、Cookie 或密钥。
- 明确 MCP Server 可访问的数据范围及可能产生的副作用。
- 对具有写入、删除或外发能力的工具标注权限要求。
