
# Fashion Design Evaluation System

一个现代化的时尚设计评估系统，具有丰富的动画效果和出色的用户体验。

## ✨ 特性

### 🎬 动画效果
- **页面过渡动画**：流畅的路由切换效果
- **数字滚动动画**：分数从 0 动态滚动到目标值
- **卡片交互动画**：悬停、点击的即时反馈
- **列表顺序动画**：内容依次淡入，避免突兀
- **玻璃态效果**：半透明模糊的导航栏
- **彩色阴影**：悬停时的视觉增强

### 📊 功能页面
- **Image Details**：设计案例详情展示，支持轮播切换
- **Score Statistics**：综合评分统计，支持数据可视化
- **Theme Analysis**：主题整体分析和评估

### 🎨 技术栈
- **React 18.3.1** - 现代化 UI 框架
- **TypeScript** - 类型安全
- **Vite 6.3.5** - 极速构建工具
- **Framer Motion** - 流畅动画库
- **Tailwind CSS 4.x** - 实用优先的样式框架
- **Radix UI** - 无障碍组件库

## 🚀 快速开始

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

服务器将在 http://localhost:3000 启动，并自动打开浏览器。

### 构建生产版本
```bash
npm run build
```

## 📖 动画文档

- [动画特性完整文档](./ANIMATIONS.md) - 详细的动画实现说明
- [快速参考指南](./ANIMATION_FEATURES.md) - 动画效果快速查看

## 🎯 项目结构

```
src/
├── components/          # React 组件
│   ├── ImageDetailPage.tsx       # 图片详情页
│   ├── ScoreStatisticsPage.tsx   # 统计页面
│   └── ui/             # UI 组件库
├── data/               # 模拟数据
├── utils/              # 工具函数
│   └── animations.ts   # 动画配置
├── App.tsx             # 主应用组件
└── index.css           # 全局样式
```

## 🎨 动画效果预览

访问以下页面体验动画：
- **主页**：http://localhost:3000/
- **统计页面**：http://localhost:3000/statistics

### 主要动画效果
1. **页面加载**：顺序淡入，分层显示
2. **图片切换**：左右滑动过渡
3. **分数显示**：数字滚动动画
4. **表格交互**：悬停高亮，单元格弹出
5. **卡片效果**：抬升阴影增强

## 💡 使用建议

- 建议使用现代浏览器（Chrome、Firefox、Safari、Edge）
- 移动端自动优化部分动画效果
- 支持暗色模式（预留）
- 响应式设计，适配各种屏幕尺寸

## 🔧 自定义配置

### 修改动画时长
编辑 `src/utils/animations.ts` 中的配置：

```typescript
export const smoothTransition = {
  duration: 0.3,  // 修改此值
  ease: "easeInOut"
};
```

### 修改开发服务器端口
编辑 `vite.config.ts`：

```typescript
server: {
  port: 3000,  // 修改端口
  open: true
}
```

## 📝 原始项目

This is a code bundle for Sneaker Product Page. The original project is available at https://www.figma.com/design/7LhHUd7S4QtMlGkOrFSxvC/Sneaker-Product-Page.

## 📄 License

MIT
