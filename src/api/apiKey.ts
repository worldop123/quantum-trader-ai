import apiClient from './request'

export interface APIKey {
  id: number
  name: string
  exchange: string
  api_key_masked: string
  is_demo: boolean
  is_active: boolean
  last_verified_at?: string
  created_at: string
}

export interface APIKeyCreate {
  name: string
  exchange: string
  api_key: string
  api_secret: string
  passphrase?: string
  is_demo: boolean
}

export interface APIKeyUpdate {
  name?: string
  api_key?: string
  api_secret?: string
  passphrase?: string
  is_demo?: boolean
  is_active?: boolean
}

export interface APIKeyVerifyResponse {
  success: boolean
  message: string
  balance?: number
}

// 获取API密钥列表
export function getAPIKeys(): Promise<APIKey[]> {
  return apiClient.get('/user/api-keys')
}

// 创建API密钥
export function createAPIKey(data: APIKeyCreate): Promise<APIKey> {
  return apiClient.post('/user/api-keys', data)
}

// 更新API密钥
export function updateAPIKey(keyId: number, data: APIKeyUpdate): Promise<APIKey> {
  return apiClient.put(`/user/api-keys/${keyId}`, data)
}

// 删除API密钥
export function deleteAPIKey(keyId: number): Promise<{ success: boolean; message: string }> {
  return apiClient.delete(`/user/api-keys/${keyId}`)
}

// 验证API密钥
export function verifyAPIKey(keyId: number): Promise<APIKeyVerifyResponse> {
  return apiClient.post(`/user/api-keys/${keyId}/verify`)
}
