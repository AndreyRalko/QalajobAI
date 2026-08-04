import {
  loginApi,
  registerApi,
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

// ==========================================
// РЕГИСТРАЦИЯ И АВТОРИЗАЦИЯ ЧЕРЕЗ EMAIL/ПАРОЛЬ
// ==========================================

export const registerUser = async (
  name: string,
  email: string,
  password: string,
  role: string,
  rememberMe: boolean = true
) => {
  const data = await registerApi(
    name,
    email,
    password,
    role as "student" | "employer"
  );

  setSession(
    { access: data.access, refresh: data.refresh },
    data.user.role,
    rememberMe
  );

  return data.user;
};

export const loginUser = async (
  email: string,
  password: string,
  rememberMe: boolean = true
) => {
  const data = await loginApi(email, password);

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