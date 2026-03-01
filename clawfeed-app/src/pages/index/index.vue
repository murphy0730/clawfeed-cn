<template>
  <view class="container">
    <!-- Tab bar: 4h / daily / weekly / monthly -->
    <view class="tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        class="tab"
        :class="{ active: currentType === tab.value }"
        @click="currentType = tab.value"
      >
        {{ tab.label }}
      </view>
    </view>

    <!-- Digest list -->
    <scroll-view
      scroll-y
      class="digest-list"
      @scrolltolower="loadMore"
    >
      <view v-if="loading && !digests.length" class="loading">加载中...</view>
      <view v-for="item in digests" :key="item.id" class="digest-card" @click="goDetail(item.id)">
        <view class="digest-header">
          <text class="digest-type">{{ digestTypeLabel(item.type) }}</text>
          <text class="digest-time">{{ timeAgo(item.created_at) }}</text>
        </view>
        <text class="digest-content">{{ truncate(item.content, 200) }}</text>
      </view>
      <view v-if="!loading && !digests.length" class="empty">暂无摘要</view>
      <view v-if="loadingMore" class="loading">加载更多...</view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useApi } from "../../composables/useApi";
import { timeAgo, truncate, digestTypeLabel } from "../../utils/format";

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
const offset = ref(0);
const PAGE_SIZE = 20;

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
  } catch (e) {
    console.error("Failed to load digests", e);
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
}

function loadMore() {
  if (!loadingMore.value) {
    fetchDigests(true);
  }
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/digest/detail?id=${id}` });
}

watch(currentType, () => fetchDigests());
onMounted(() => fetchDigests());
</script>

<style scoped>
.container {
  padding: 0;
}
.tabs {
  display: flex;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  font-size: 28rpx;
  color: #666;
  position: relative;
}
.tab.active {
  color: #333;
  font-weight: 600;
}
.tab.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 30%;
  right: 30%;
  height: 4rpx;
  background: #333;
  border-radius: 2rpx;
}
.digest-list {
  height: calc(100vh - 88rpx - 100rpx);
}
.digest-card {
  margin: 16rpx 24rpx;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}
.digest-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}
.digest-type {
  font-size: 24rpx;
  color: #1890ff;
  font-weight: 500;
}
.digest-time {
  font-size: 22rpx;
  color: #999;
}
.digest-content {
  font-size: 26rpx;
  color: #333;
  line-height: 1.6;
}
.loading,
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
