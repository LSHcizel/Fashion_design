// 动画配置和变体
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};

export const slideInRight = {
  initial: { opacity: 0, x: 50 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 }
};

export const slideInLeft = {
  initial: { opacity: 0, x: -50 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 50 }
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05
    }
  }
};

export const listItem = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 }
};

// 弹簧动画配置
export const springTransition = {
  type: "spring",
  stiffness: 300,
  damping: 30
};

export const smoothTransition = {
  duration: 0.3,
  ease: "easeInOut"
};

// 数字滚动动画
export const numberAnimation = {
  initial: { opacity: 0, scale: 0.5 },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 25
    }
  }
};

// 卡片悬停效果
export const cardHover = {
  scale: 1.02,
  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)",
  transition: { duration: 0.2 }
};

// 按钮点击效果
export const buttonTap = {
  scale: 0.95
};

// 进度条动画
export const progressBar = {
  initial: { scaleX: 0, originX: 0 },
  animate: { scaleX: 1 },
  transition: { duration: 0.8, ease: "easeOut" }
};
