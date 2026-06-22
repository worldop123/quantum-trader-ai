import apiClient from './request'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface UserInfo {
  id: number
  email: string
  username: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  theme: string
  language: string
  rise_color: string
  fall_color: string
  notification_enabled: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

// 登录
export function login(data: LoginRequest): Promise<LoginResponse> {
  return apiClient.post('/auth/login', data)
}

// 注册
export function register(data: RegisterRequest): Promise<LoginResponse> {
  return apiClient.post('/auth/register', data)
}

// 获取当前用户信息
export function getCurrentUser(): Promise<UserInfo> {
  return apiClient.get('/auth/me')
}

// 刷新token
export function refreshToken(): Promise<LoginResponse> {
  return apiClient.post('/auth/refresh')
}

// 更新用户设置
export function updateSettings(data: Partial<UserInfo>): Promise<UserInfo> {
  return apiClient.put('/user/settings', data)
}

// 获取用户设置
export function getSettings(): Promise<UserInfo> {
  return apiClient.get('/user/settings')
}
