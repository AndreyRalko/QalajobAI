import {
  loginApi,
  getMe,
  forgotPasswordApi,
  resetPasswordApi,
  verifyEmailApi,
  resendVerificationApi,
} from "@/lib/api";

import {
  clearSession,
  setSession,
  getAccessToken,
} from "@/lib/session";

export const loginUser = async (
  login: string,
  password: string,
  rememberMe: boolean = true
) => {
  const data = await loginApi(login, password);

  setSession(
    { access: data.access, refresh: data.refresh },
    data.user.role,
    rememberMe
  );

  return data.user;
};

export const logoutUser = async () => {
  clearSession();
};

// ==========================================
// РАБОТА С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ
// ==========================================

export const getUserRole = async () => {
  const token = getAccessToken();

  if (!token) {
    return null;
  }

  try {
    const user = await getMe(token);

    return {
      name: user.name,
      email: user.email,
      role: user.role,
      studentId: user.student_id,
      subscription: user.subscription,
      language: user.language,
      isBanned: user.is_banned,
      emailVerified: user.email_verified,
    };
  } catch {
    return null;
  }
};

// ==========================================
// ВОССТАНОВЛЕНИЕ ПАРОЛЯ И ПОДТВЕРЖДЕНИЕ EMAIL
// ==========================================

export const forgotPassword = async (email: string) => {
  return forgotPasswordApi(email);
};

export const resetPassword = async (token: string, newPassword: string) => {
  return resetPasswordApi(token, newPassword);
};

export const verifyEmail = async (token: string) => {
  return verifyEmailApi(token);
};

export const resendVerification = async () => {
  return resendVerificationApi();
};

// ==========================================
// АВТОРИЗАЦИЯ ЧЕРЕЗ GOOGLE (ОБНОВЛЕННАЯ)
// ==========================================

export const googleLogin = async () => {
  throw new Error("GOOGLE_LOGIN_DISABLED");
};