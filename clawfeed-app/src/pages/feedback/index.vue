<template>
  <view class="container">
    <!-- Submit new feedback -->
    <view class="form-section">
      <textarea
        v-model="message"
        class="textarea"
        placeholder="写下你的反馈或建议..."
        :maxlength="1000"
      />
      <button class="btn-submit" :loading="submitting" @click="submit">
        提交反馈
      </button>
    </view>

    <!-- Feedback history -->
    <view class="section-title">历史反馈</view>
    <view v-if="loading" class="loading">加载中...</view>
    <view v-for="item in feedbackList" :key="item.id" class="feedback-card">
      <text class="fb-message">{{ item.message }}</text>
      <text class="fb-time">{{ item.created_at }}</text>
      <view v-if="item.reply" class="fb-reply">
        <text class="reply-label">回复：</text>
        <text class="reply-text">{{ item.reply }}</text>
      </view>
    </view>
    <view v-if="!loading && !feedbackList.length" class="empty">
      暂无反馈记录
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useApi } from "../../composables/useApi";

const api = useApi();
const message = ref("");
const submitting = ref(false);
const loading = ref(true);
const feedbackList = ref([]);

async function fetchFeedback() {
  loading.value = true;
  try {
    const data = await api.getFeedback();
    feedbackList.value = data.feedback || [];
    if (data.unread > 0) {
      await api.markFeedbackRead();
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function submit() {
  const msg = message.value.trim();
  if (!msg) {
    uni.showToast({ title: "请输入反馈内容", icon: "none" });
    return;
  }
  submitting.value = true;
  try {
    await api.createFeedback({ message: msg });
    uni.showToast({ title: "提交成功", icon: "success" });
    message.value = "";
    fetchFeedback();
  } catch (e) {
    uni.showToast({ title: "提交失败", icon: "none" });
  } finally {
    submitting.value = false;
  }
}

onMounted(() => fetchFeedback());
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.form-section {
  margin-bottom: 32rpx;
}
.textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background: #fff;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: 1px solid #e8e8e8;
  box-sizing: border-box;
  margin-bottom: 16rpx;
}
.btn-submit {
  background: #1890ff;
  color: #fff;
  border: none;
}
.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}
.feedback-card {
  padding: 24rpx;
  margin-bottom: 12rpx;
  background: #fff;
  border-radius: 12rpx;
}
.fb-message {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}
.fb-time {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
}
.fb-reply {
  background: #f6f8fa;
  padding: 16rpx;
  border-radius: 8rpx;
}
.reply-label {
  font-size: 24rpx;
  color: #1890ff;
  font-weight: 500;
}
.reply-text {
  font-size: 26rpx;
  color: #333;
}
.loading,
.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
