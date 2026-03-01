<template>
  <view class="container">
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else-if="digest" class="detail">
      <view class="header">
        <text class="type">{{ digestTypeLabel(digest.type) }}</text>
        <text class="time">{{ formatDate(digest.created_at) }}</text>
      </view>
      <view class="content">
        <rich-text :nodes="digest.content"></rich-text>
      </view>
      <view class="actions">
        <button class="btn-mark" size="mini" @click="toggleMark">
          {{ marked ? "已收藏" : "收藏" }}
        </button>
      </view>
    </view>
    <view v-else class="empty">摘要不存在</view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import { formatDate, digestTypeLabel } from "../../utils/format";

const api = useApi();
const digest = ref(null);
const loading = ref(true);
const marked = ref(false);
let digestId = null;

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

<style scoped>
.container {
  padding: 24rpx;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}
.type {
  font-size: 28rpx;
  color: #1890ff;
  font-weight: 600;
}
.time {
  font-size: 24rpx;
  color: #999;
}
.content {
  background: #fff;
  padding: 24rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  line-height: 1.8;
  color: #333;
}
.actions {
  margin-top: 32rpx;
  display: flex;
  justify-content: center;
}
.btn-mark {
  background: #1890ff;
  color: #fff;
  border: none;
  font-size: 26rpx;
}
.loading,
.empty {
  text-align: center;
  padding: 60rpx;
  color: #999;
}
</style>
