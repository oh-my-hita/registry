# OH-MY-HITA 官方插件 Registry

当前发布 19 个官方 UI 插件（T2 APK）：

- 来源：`oh-my-hita/ui-*`
- API：12（3.3.1 插件与 preset 需要宿主 0.10.3+）
- 每个条目包含版本、APK URL、sha256 与大小

`timetable/eas/resource/user/theta` 仍是 privileged builtin，迁移完成前不进入本 registry。

`hita-android-3.3.1` 使用 `plugins-0.10.3` release 中的校园/待办 dex 与 UI APK。

刷新：

```bash
curl -L https://raw.githubusercontent.com/oh-my-hita/registry/main/registry/index.json
```
