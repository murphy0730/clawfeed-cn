<template>
  <view class="page-container">
    <!-- Submit section -->
    <view class="submit-section">
      <view class="input-wrapper">
        <textarea
          v-model="message"
          class="feedback-input"
          placeholder="写下你的反馈或建议..."
          placeholder-class="input-placeholder"
          :maxlength="1000"
        />
        <view class="char-count">
          <text class="count-text">{{ message.length }}/1000</text>
        </view>
      </view>
      <view
        class="submit-btn"
        :class="{ disabled: !message.trim() || submitting }"
        @click="submit"
      >
        <text v-if="!submitting" class="submit-text">提交反馈</text>
        <view v-else class="submit-spinner"></view>
      </view>
    </view>

    <!-- Feedback history -->
    <view class="history-section">
      <view class="section-header">
        <text class="section-title">历史反馈</text>
      </view>

      <!-- Loading -->
      <view v-if="loading" class="loading-wrapper">
        <XLoading text="加载中..." :size="48" />
      </view>

      <!-- Empty -->
      <XEmpty
        v-else-if="!feedbackList.length"
        icon="💬"
        title="暂无反馈记录"
        description="你的反馈会帮助我们做得更好"
      />

      <!-- Feedback list -->
      <view v-else class="feedback-list">
        <view
          v-for="(item, index) in feedbackList"
          :key="item.id"
          class="feedback-card"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="feedback-header">
            <text class="feedback-time">{{ formatDate(item.created_at) }}</text>
          </view>
          <text class="feedback-message">{{ item.message }}</text>
          <view v-if="item.reply" class="reply-section">
            <view class="reply-header">
              <text class="reply-label">官方回复</text>
            </view>
            <text class="reply-text">{{ item.reply }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom padding -->
    <view class="bottom-padding"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useApi } from "../../composables/useApi";
import XLoading from "../../components/XLoading.vue";
import XEmpty from "../../components/XEmpty.vue";

const api = useApi();
const message = ref("");
const submitting = ref(false);
const loading = ref(true);
const feedbackList = ref([]);

function formatDate(dateStr) {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

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
  if (!msg || submitting.value) return;

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

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
}

.submit-section {
  padding: 24rpx;
  background: #13131a;
  border-bottom: 1px solid #2a2a3a;
}

.input-wrapper {
  margin-bottom: 16rpx;
}

.feedback-input {
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  background: #0a0a0f;
  border: 1px solid #2a2a3a;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #e8e8f0;
  line-height: 1.6;
  box-sizing: border-box;
  transition: all 0.25s ease;
}

.feedback-input:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.15);
}

.input-placeholder {
  color: #5a5a70;
}

.char-count {
  display: flex;
  justify-content: flex-end;
  margin-top: 8rpx;
}

.count-text {
  font-size: 22rpx;
  color: #5a5a70;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx 0;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 16rpx;
  transition: all 0.25s ease;
}

.submit-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.submit-btn.disabled {
  opacity: 0.5;
}

.submit-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
}

.submit-spinner {
  width: 36rpx;
  height: 36rpx;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.history-section {
  padding: 24rpx;
}

.section-header {
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #e8e8f0;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 48rpx 0;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.feedback-card {
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  animation: fade-in 0.3s ease-out backwards;
}

.feedback-header {
  margin-bottom: 12rpx;
}

.feedback-time {
  font-size: 22rpx;
  color: #5a5a70;
}

.feedback-message {
  display: block;
  font-size: 28rpx;
  color: #e8e8f0;
  line-height: 1.7;
}

.reply-section {
  margin-top: 16rpx;
  padding: 16rpx;
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12rpx;
}

.reply-header {
  margin-bottom: 8rpx;
}

.reply-label {
  font-size: 22rpx;
  color: #00d4ff;
  font-weight: 600;
}

.reply-text {
  display: block;
  font-size: 26rpx;
  color: #e8e8f0;
  line-height: 1.6;
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