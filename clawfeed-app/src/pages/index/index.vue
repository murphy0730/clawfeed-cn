<template>
  <view class="page-container">
    <!-- Header with brand -->
    <view class="header">
      <view class="brand">
        <text class="brand-icon">⚡</text>
        <text class="brand-name gradient-text">ClawFeed</text>
      </view>
      <text class="brand-tagline">AI 驱动的新闻摘要</text>
    </view>

    <!-- Tab bar: 4h / daily / weekly / monthly -->
    <view class="tabs-container">
      <view class="tabs">
        <view
          v-for="(tab, index) in tabs"
          :key="tab.value"
          class="tab"
          :class="{ active: currentType === tab.value }"
          :style="{ animationDelay: index * 0.05 + 's' }"
          @click="currentType = tab.value"
        >
          <text class="tab-label">{{ tab.label }}</text>
        </view>
      </view>
    </view>

    <!-- Digest list -->
    <scroll-view
      scroll-y
      class="digest-scroll"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <!-- Loading skeleton -->
      <view v-if="loading && !digests.length" class="skeleton-list">
        <view v-for="i in 4" :key="i" class="skeleton-card">
          <view class="skeleton-header">
            <view class="skeleton-tag skeleton"></view>
            <view class="skeleton-time skeleton"></view>
          </view>
          <view class="skeleton-content">
            <view class="skeleton-line skeleton"></view>
            <view class="skeleton-line skeleton" style="width: 80%"></view>
            <view class="skeleton-line skeleton" style="width: 60%"></view>
          </view>
        </view>
      </view>

      <!-- Digest cards -->
      <view v-else>
        <view
          v-for="(item, index) in digests"
          :key="item.id"
          class="digest-card"
          :style="{ animationDelay: index * 0.05 + 's' }"
          @click="goDetail(item.id)"
        >
          <view class="card-header">
            <view class="type-badge" :class="getTypeClass(item.type)">
              <text class="type-icon">{{ getTypeIcon(item.type) }}</text>
              <text class="type-text">{{ digestTypeLabel(item.type) }}</text>
            </view>
            <text class="time-text">{{ timeAgo(item.created_at) }}</text>
          </view>
          <view class="card-content">
            <text class="content-text">{{ truncate(item.content, 150) }}</text>
          </view>
          <view class="card-footer">
            <view class="footer-line"></view>
          </view>
        </view>
      </view>

      <!-- Empty state -->
      <XEmpty
        v-if="!loading && !digests.length"
        icon="📭"
        title="暂无摘要"
        description="还没有生成此类型的摘要，请稍后再来查看"
      />

      <!-- Load more indicator -->
      <view v-if="loadingMore" class="load-more">
        <XLoading text="加载中..." :size="48" />
      </view>

      <!-- End of list -->
      <view v-if="!loading && !loadingMore && digests.length && !hasMore" class="end-marker">
        <view class="end-line"></view>
        <text class="end-text">已经到底了</text>
        <view class="end-line"></view>
      </view>

      <!-- Bottom padding for tab bar -->
      <view class="bottom-padding"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useApi } from "../../composables/useApi";
import { timeAgo, truncate, digestTypeLabel } from "../../utils/format";
import XEmpty from "../../components/XEmpty.vue";
import XLoading from "../../components/XLoading.vue";

const api = useApi();

const tabs = [
  { label: "4小时", value: "4h" },
  { label: "日报", value: "daily" },
  { label: "周报", value: "weekly" },
  { label: "月报", value: "monthly" },
];

const currentType = ref("4h");
const digests = ref([]);
const loading = ref(false);
const loadingMore = ref(false);
const refreshing = ref(false);
const offset = ref(0);
const hasMore = ref(true);
const PAGE_SIZE = 20;

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

async function fetchDigests(append = false) {
  if (append) {
    loadingMore.value = true;
  } else {
    loading.value = true;
    offset.value = 0;
    digests.value = [];
  }
  try {
    const data = await api.getDigests({
      type: currentType.value,
      limit: PAGE_SIZE,
      offset: offset.value,
    });
    if (append) {
      digests.value = [...digests.value, ...data];
    } else {
      digests.value = data;
    }
    offset.value += data.length;
    hasMore.value = data.length === PAGE_SIZE;
  } catch (e) {
    console.error("Failed to load digests", e);
  } finally {
    loading.value = false;
    loadingMore.value = false;
    refreshing.value = false;
  }
}

async function onRefresh() {
  refreshing.value = true;
  await fetchDigests();
}

function loadMore() {
  if (!loadingMore.value && hasMore.value) {
    fetchDigests(true);
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/digest/detail?id=${id}` });
}

watch(currentType, () => {
  hasMore.value = true;
  fetchDigests();
});
onMounted(() => fetchDigests());
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
}

.header {
  padding: 32rpx 24rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.brand-icon {
  font-size: 40rpx;
}

.brand-name {
  font-size: 40rpx;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-tagline {
  font-size: 24rpx;
  color: #8888a0;
}

.tabs-container {
  padding: 0 24rpx 16rpx;
}

.tabs {
  display: flex;
  gap: 12rpx;
  padding: 6rpx;
  background: #13131a;
  border-radius: 16rpx;
  border: 1px solid #2a2a3a;
}

.tab {
  flex: 1;
  padding: 16rpx 0;
  text-align: center;
  border-radius: 12rpx;
  transition: all 0.25s ease;
  animation: fade-in 0.3s ease-out backwards;
}

.tab.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(168, 85, 247, 0.15));
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.tab-label {
  font-size: 26rpx;
  font-weight: 500;
  color: #8888a0;
  transition: color 0.25s ease;
}

.tab.active .tab-label {
  color: #00d4ff;
}

.digest-scroll {
  height: calc(100vh - 240rpx);
}

.digest-card {
  margin: 0 24rpx 16rpx;
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  transition: all 0.25s ease;
  animation: fade-in 0.3s ease-out backwards;
}

.digest-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.type-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
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
  font-size: 22rpx;
}

.type-text {
  font-size: 22rpx;
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
  font-size: 22rpx;
  color: #5a5a70;
}

.card-content {
  margin-bottom: 16rpx;
}

.content-text {
  font-size: 28rpx;
  color: #e8e8f0;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: center;
}

.footer-line {
  width: 48rpx;
  height: 4rpx;
  background: linear-gradient(90deg, #00d4ff, #a855f7);
  border-radius: 2rpx;
  opacity: 0.3;
}

// Skeleton styles
.skeleton-list {
  padding: 0 24rpx;
}

.skeleton-card {
  margin-bottom: 16rpx;
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.skeleton-tag {
  width: 100rpx;
  height: 36rpx;
  border-radius: 8rpx;
}

.skeleton-time {
  width: 80rpx;
  height: 28rpx;
  border-radius: 6rpx;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.skeleton-line {
  height: 28rpx;
  border-radius: 6rpx;
}

.load-more {
  padding: 32rpx;
  display: flex;
  justify-content: center;
}

.end-marker {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32rpx 24rpx;
  gap: 24rpx;
}

.end-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, #2a2a3a, transparent);
}

.end-text {
  font-size: 24rpx;
  color: #5a5a70;
}

.bottom-padding {
  height: 32rpx;
}

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
</style>