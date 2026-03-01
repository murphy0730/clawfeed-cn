<template>
  <view class="container">
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else>
      <view v-if="!marks.length" class="empty">暂无收藏</view>
      <view v-for="item in marks" :key="item.id" class="mark-card">
        <view class="mark-info">
          <text class="mark-title">{{ item.title || item.url }}</text>
          <text class="mark-time">{{ timeAgo(item.created_at) }}</text>
        </view>
        <view class="mark-actions">
          <text class="btn-delete" @click="removeMark(item.id)">删除</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import { timeAgo } from "../../utils/format";

const api = useApi();
const marks = ref([]);
const loading = ref(true);

async function fetchMarks() {
  loading.value = true;
  try {
    const data = await api.getMarks();
    marks.value = Array.isArray(data) ? data : [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function removeMark(id) {
  uni.showModal({
    title: "确认删除",
    content: "确定要删除这条收藏吗？",
    success: async (res) => {
      if (res.confirm) {
        await api.deleteMark(id);
        marks.value = marks.value.filter((m) => m.id !== id);
        uni.showToast({ title: "已删除", icon: "success" });
      }
    },
  });
}

onShow(() => fetchMarks());
onMounted(() => fetchMarks());
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.mark-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: #fff;
  border-radius: 16rpx;
}
.mark-info {
  flex: 1;
}
.mark-title {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}
.mark-time {
  font-size: 22rpx;
  color: #999;
}
.btn-delete {
  font-size: 24rpx;
  color: #ff4d4f;
  padding: 8rpx 16rpx;
}
.loading,
.empty {
  text-align: center;
  padding: 60rpx;
  color: #999;
}
</style>
