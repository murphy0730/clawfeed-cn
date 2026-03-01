<template>
  <view class="page-container">
    <!-- Loading state -->
    <view v-if="loading" class="loading-wrapper">
      <XLoading text="加载中..." :size="64" />
    </view>

    <!-- Content -->
    <view v-else-if="digest" class="content-wrapper">
      <!-- Header with gradient -->
      <view class="header">
        <view class="header-bg"></view>
        <view class="header-content">
          <view class="type-badge" :class="getTypeClass(digest.type)">
            <text class="type-icon">{{ getTypeIcon(digest.type) }}</text>
            <text class="type-text">{{ digestTypeLabel(digest.type) }}</text>
          </view>
          <text class="time-text">{{ formatDate(digest.created_at) }}</text>
        </view>
      </view>

      <!-- Main content -->
      <view class="main-content">
        <view class="content-card">
          <rich-text class="rich-content" :nodes="digest.content"></rich-text>
        </view>
      </view>

      <!-- Action bar -->
      <view class="action-bar">
        <view
          class="action-btn"
          :class="{ active: marked }"
          @click="toggleMark"
        >
          <text class="action-icon">{{ marked ? '★' : '☆' }}</text>
          <text class="action-label">{{ marked ? '已收藏' : '收藏' }}</text>
        </view>
      </view>
    </view>

    <!-- Empty state -->
    <XEmpty
      v-else
      icon="📄"
      title="摘要不存在"
      description="该摘要可能已被删除或不存在"
    />
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import { formatDate, digestTypeLabel } from "../../utils/format";
import XLoading from "../../components/XLoading.vue";
import XEmpty from "../../components/XEmpty.vue";

const api = useApi();
const digest = ref(null);
const loading = ref(true);
const marked = ref(false);
let digestId = null;

function getTypeClass(type) {
  const classes = {
    "4h": "cyan",
    daily: "purple",
    weekly: "green",
    monthly: "orange",
  };
  return classes[type] || "cyan";
}

function getTypeIcon(type) {
  const icons = {
    "4h": "⚡",
    daily: "📅",
    weekly: "📊",
    monthly: "📈",
  };
  return icons[type] || "📄";
}

onLoad((query) => {
  digestId = query.id;
});

onMounted(async () => {
  if (!digestId) return;
  try {
    digest.value = await api.getDigest(digestId);
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

async function toggleMark() {
  if (marked.value) return;
  try {
    await api.createMark({
      url: `clawfeed://digest/${digestId}`,
      title: `${digestTypeLabel(digest.value.type)} - ${digest.value.created_at}`,
    });
    marked.value = true;
    uni.showToast({ title: "已收藏", icon: "success" });
  } catch (e) {
    uni.showToast({ title: "收藏失败", icon: "none" });
  }
}
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}

.content-wrapper {
  min-height: 100vh;
}

.header {
  position: relative;
  padding: 32rpx 24rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(168, 85, 247, 0.1));
  opacity: 0.5;
}

.header-content {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  border-radius: 12rpx;
  background: rgba(0, 212, 255, 0.12);
}

.type-badge.cyan {
  background: rgba(0, 212, 255, 0.12);
}

.type-badge.purple {
  background: rgba(168, 85, 247, 0.12);
}

.type-badge.green {
  background: rgba(34, 197, 94, 0.12);
}

.type-badge.orange {
  background: rgba(245, 158, 11, 0.12);
}

.type-icon {
  font-size: 28rpx;
}

.type-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #00d4ff;
}

.type-badge.purple .type-text {
  color: #a855f7;
}

.type-badge.green .type-text {
  color: #22c55e;
}

.type-badge.orange .type-text {
  color: #f59e0b;
}

.time-text {
  font-size: 24rpx;
  color: #8888a0;
}

.main-content {
  padding: 0 24rpx;
}

.content-card {
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  padding: 32rpx;
}

.rich-content {
  font-size: 30rpx;
  color: #e8e8f0;
  line-height: 1.9;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx;
  background: rgba(10, 10, 15, 0.95);
  border-top: 1px solid #2a2a3a;
  display: flex;
  justify-content: center;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 20rpx 48rpx;
  background: transparent;
  border: 1px solid #00d4ff;
  border-radius: 16rpx;
  transition: all 0.25s ease;
}

.action-btn:active,
.action-btn.active {
  background: rgba(0, 212, 255, 0.15);
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.3);
}

.action-btn.active {
  border-color: #a855f7;
  background: rgba(168, 85, 247, 0.15);
  box-shadow: 0 0 20rpx rgba(168, 85, 247, 0.3);
}

.action-icon {
  font-size: 36rpx;
  color: #00d4ff;
}

.action-btn.active .action-icon {
  color: #a855f7;
}

.action-label {
  font-size: 28rpx;
  font-weight: 500;
  color: #e8e8f0;
}
</style>