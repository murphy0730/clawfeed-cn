<template>
  <view class="page-container">
    <!-- Loading state -->
    <view v-if="loading" class="loading-wrapper">
      <XLoading text="加载中..." :size="64" />
    </view>

    <!-- Marks list -->
    <view v-else class="content-wrapper">
      <!-- Empty state -->
      <XEmpty
        v-if="!marks.length"
        icon="☆"
        title="暂无收藏"
        description="在摘要详情页点击收藏按钮，即可添加到这里"
      />

      <!-- Mark cards -->
      <view v-else class="marks-list">
        <view
          v-for="(item, index) in marks"
          :key="item.id"
          class="mark-card"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="card-content" @click="openMark(item)">
            <text class="mark-title">{{ item.title || item.url }}</text>
            <text class="mark-time">{{ timeAgo(item.created_at) }}</text>
          </view>
          <view class="card-actions">
            <view class="delete-btn" @click="removeMark(item.id)">
              <text class="delete-icon">×</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Bottom padding -->
      <view class="bottom-padding"></view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import { timeAgo } from "../../utils/format";
import XLoading from "../../components/XLoading.vue";
import XEmpty from "../../components/XEmpty.vue";

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

function openMark(item) {
  // Parse clawfeed://digest/123 format
  if (item.url && item.url.startsWith("clawfeed://digest/")) {
    const id = item.url.replace("clawfeed://digest/", "");
    uni.navigateTo({ url: `/pages/digest/detail?id=${id}` });
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
  padding: 24rpx;
}

.marks-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.mark-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  transition: all 0.25s ease;
  animation: fade-in 0.3s ease-out backwards;
}

.mark-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.mark-title {
  display: block;
  font-size: 28rpx;
  color: #e8e8f0;
  font-weight: 500;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mark-time {
  display: block;
  font-size: 22rpx;
  color: #5a5a70;
}

.card-actions {
  padding-left: 16rpx;
}

.delete-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12rpx;
  transition: all 0.25s ease;
}

.delete-btn:active {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
}

.delete-icon {
  font-size: 36rpx;
  color: #ef4444;
  line-height: 1;
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