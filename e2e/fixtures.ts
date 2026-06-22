import { test as baseTest, expect } from '@playwright/test';

// 扩展基础test，添加自定义登录fixture
export const test = baseTest.extend({
  // 普通用户登录fixture
  authenticatedUser: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@quantumtrader.ai');
    await page.fill('input[type="password"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('/dashboard');
    await use(page);
  },
  
  // 管理员登录fixture
  authenticatedAdmin: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@quantumtrader.ai');
    await page.fill('input[type="password"]', 'Admin123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('/admin/dashboard');
    await use(page);
  },
});

export { expect };
