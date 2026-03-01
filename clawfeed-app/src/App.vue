<script setup>
import { onLaunch } from "@dcloudio/uni-app";
import { useUserStore } from "./store/user";

onLaunch(() => {
  const userStore = useUserStore();
  userStore.checkLogin();
});
</script>

<style lang="scss">
@use "./uni.scss" as *;

// Global Page Styles
// ==================
page {
  background-color: $color-bg-primary;
  font-family: $font-family;
  color: $color-text-primary;
  font-size: $font-size-base;
  line-height: $line-height-normal;
}

// Base View Styles
// ================
.container {
  min-height: 100vh;
  background-color: $color-bg-primary;
}

// Typography
// ==========
.text-primary {
  color: $color-text-primary;
}

.text-secondary {
  color: $color-text-secondary;
}

.text-tertiary {
  color: $color-text-tertiary;
}

.text-neon-cyan {
  color: $color-neon-cyan;
}

.text-neon-purple {
  color: $color-neon-purple;
}

.text-neon-green {
  color: $color-neon-green;
}

// Gradient Text
.gradient-text {
  background: $gradient-primary;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

// Card Styles
// ===========
.cyber-card {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
  transition: all $transition-normal;

  &:active {
    transform: scale(0.98);
    border-color: $color-neon-cyan;
  }
}

// Glassmorphism Card (H5 only - fallback for MP)
// #ifdef H5
.glass-card {
  background: rgba(19, 19, 26, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(42, 42, 58, 0.6);
  border-radius: $radius-lg;
}
// #endif

// MP fallback for glass card
// #ifndef H5
.glass-card {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
}
// #endif

// Neon Glow Effects
// =================
.neon-border {
  position: relative;

  &::before {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    padding: 1px;
    background: $gradient-primary;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }
}

.neon-glow-cyan {
  box-shadow: $shadow-glow-cyan;
}

.neon-glow-purple {
  box-shadow: $shadow-glow-purple;
}

// Button Styles
// =============
.btn-neon {
  background: transparent;
  border: 1px solid $color-neon-cyan;
  color: $color-neon-cyan;
  border-radius: $radius-md;
  padding: $spacing-sm $spacing-md;
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  transition: all $transition-normal;

  &:active {
    background: rgba(0, 212, 255, 0.1);
    box-shadow: $shadow-glow-cyan;
  }
}

.btn-neon-filled {
  background: $gradient-primary;
  border: none;
  color: #fff;
  border-radius: $radius-md;
  padding: $spacing-sm $spacing-md;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  transition: all $transition-normal;

  &:active {
    transform: scale(0.96);
    opacity: 0.9;
  }
}

.btn-ghost {
  background: transparent;
  border: 1px solid $color-border;
  color: $color-text-secondary;
  border-radius: $radius-md;
  padding: $spacing-sm $spacing-md;
  font-size: $font-size-sm;
  transition: all $transition-normal;

  &:active {
    border-color: $color-text-secondary;
    color: $color-text-primary;
  }
}

// Input Styles
// ============
.cyber-input {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  padding: $spacing-sm $spacing-md;
  color: $color-text-primary;
  font-size: $font-size-base;
  transition: all $transition-normal;

  &:focus {
    border-color: $color-neon-cyan;
    box-shadow: $shadow-glow-cyan;
  }

  &::placeholder {
    color: $color-text-tertiary;
  }
}

// Loading States
// =============
.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 3px solid $color-border;
  border-top-color: $color-neon-cyan;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// Pulse animation for neon effects
@keyframes neon-pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: $shadow-glow-cyan;
  }
  50% {
    opacity: 0.8;
    box-shadow: 0 0 30rpx rgba(0, 212, 255, 0.6);
  }
}

// Fade in animation
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(16rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fade-in 0.3s ease-out;
}

// Stagger animation for lists
@keyframes stagger-in {
  from {
    opacity: 0;
    transform: translateY(24rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Skeleton loading
// ================
.skeleton {
  background: linear-gradient(
    90deg,
    $color-bg-secondary 25%,
    $color-bg-tertiary 50%,
    $color-bg-secondary 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: $radius-sm;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

// Section Title
// =============
.section-title {
  font-size: $font-size-md;
  font-weight: $font-weight-semibold;
  color: $color-text-primary;
  margin-bottom: $spacing-sm;
  padding-left: $spacing-xs;
}

// Empty State
// ===========
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-2xl $spacing-lg;
  color: $color-text-tertiary;

  .empty-icon {
    font-size: 80rpx;
    margin-bottom: $spacing-md;
    opacity: 0.5;
  }

  .empty-text {
    font-size: $font-size-base;
    color: $color-text-secondary;
  }
}

// Type Tags
// =========
.type-tag {
  display: inline-block;
  padding: $spacing-xs $spacing-sm;
  font-size: $font-size-xs;
  font-weight: $font-weight-medium;
  border-radius: $radius-sm;
  background: rgba(0, 212, 255, 0.15);
  color: $color-neon-cyan;

  &.purple {
    background: rgba(168, 85, 247, 0.15);
    color: $color-neon-purple;
  }

  &.green {
    background: rgba(34, 197, 94, 0.15);
    color: $color-neon-green;
  }

  &.orange {
    background: rgba(245, 158, 11, 0.15);
    color: $color-neon-orange;
  }

  &.pink {
    background: rgba(236, 72, 153, 0.15);
    color: $color-neon-pink;
  }
}
</style>