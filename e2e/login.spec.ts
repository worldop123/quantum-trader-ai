import { test, expect } from './fixtures';

test.describe('登录页面 - Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('页面元素完整性检查', async ({ page }) => {
    // 检查Logo和标题
    await expect(page.locator('h1:has-text("QuantumTrader AI")')).toBeVisible();
    await expect(page.locator('text=下一代AI量化交易系统')).toBeVisible();
    
    // 检查表单元素
    await expect(page.locator('text=邮箱地址')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('text=密码')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    
    // 检查记住我和忘记密码
    await expect(page.locator('text=记住我')).toBeVisible();
    await expect(page.locator('text=忘记密码？')).toBeVisible();
    
    // 检查登录按钮
    await expect(page.locator('button:has-text("登录")')).toBeVisible();
    
    // 检查注册链接
    await expect(page.locator('text=还没有账户？')).toBeVisible();
    await expect(page.locator('text=立即注册')).toBeVisible();
    
    // 检查测试账号区域
    await expect(page.locator('text=测试账号')).toBeVisible();
    await expect(page.locator('text=普通用户')).toBeVisible();
    await expect(page.locator('text=管理员')).toBeVisible();
  });

  test('普通用户登录成功 - 正常流程', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@quantumtrader.ai');
    await page.fill('input[type="password"]', 'Test123456');
    await page.click('button:has-text("登录")');
    
    await page.waitForURL('/dashboard');
    await expect(page).toHaveURL('/dashboard');
    
    // 验证登录成功后显示用户信息
    await expect(page.locator('text=模拟盘')).toBeVisible();
  });

  test('管理员登录成功 - 正常流程', async ({ page }) => {
    await page.fill('input[type="email"]', 'admin@quantumtrader.ai');
    await page.fill('input[type="password"]', 'Admin123456');
    await page.click('button:has-text("登录")');
    
    await page.waitForURL('/admin/dashboard');
    await expect(page).toHaveURL('/admin/dashboard');
    
    // 验证管理员标识
    await expect(page.locator('text=管理员')).toBeVisible();
  });

  test('错误密码登录失败 - 异常流程', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@quantumtrader.ai');
    await page.fill('input[type="password"]', 'WrongPassword123');
    await page.click('button:has-text("登录")');
    
    // 应该显示错误信息
    await expect(page.locator('text=邮箱或密码错误')).toBeVisible({ timeout: 5000 });
  });

  test('空邮箱登录 - 边界情况', async ({ page }) => {
    await page.fill('input[type="password"]', 'Test123456');
    await page.click('button:has-text("登录")');
    
    // HTML5验证应该阻止提交
    const emailInput = page.locator('input[type="email"]');
    const isRequired = await emailInput.evaluate(el => el.required);
    expect(isRequired).toBeTruthy();
  });

  test('空密码登录 - 边界情况', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@quantumtrader.ai');
    await page.click('button:has-text("登录")');
    
    const passwordInput = page.locator('input[type="password"]');
    const isRequired = await passwordInput.evaluate(el => el.required);
    expect(isRequired).toBeTruthy();
  });

  test('无效邮箱格式 - 边界情况', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'Test123456');
    
    // HTML5 email验证
    const emailInput = page.locator('input[type="email"]');
    const isValid = await emailInput.evaluate(el => el.checkValidity());
    expect(isValid).toBeFalsy();
  });

  test('点击测试账号快速填充 - 普通用户', async ({ page }) => {
    await page.click('button:has-text("普通用户")');
    
    // 验证邮箱和密码被填充
    const emailValue = await page.locator('input[type="email"]').inputValue();
    expect(emailValue).toBe('test@quantumtrader.ai');
  });

  test('点击测试账号快速填充 - 管理员', async ({ page }) => {
    await page.click('button:has-text("管理员")');
    
    const emailValue = await page.locator('input[type="email"]').inputValue();
    expect(emailValue).toBe('admin@quantumtrader.ai');
  });

  test('跳转到注册页面', async ({ page }) => {
    await page.click('text=立即注册');
    await expect(page).toHaveURL('/register');
  });

  test('记住我复选框功能', async ({ page }) => {
    const checkbox = page.locator('input[type="checkbox"]').first();
    
    // 默认未选中
    expect(await checkbox.isChecked()).toBeFalsy();
    
    // 点击选中
    await checkbox.click();
    expect(await checkbox.isChecked()).toBeTruthy();
    
    // 再次点击取消
    await checkbox.click();
    expect(await checkbox.isChecked()).toBeFalsy();
  });

  test('登录加载状态', async ({ page }) => {
    await page.fill('input[type="email"]', 'test@quantumtrader.ai');
    await page.fill('input[type="password"]', 'Test123456');
    
    // 点击登录后按钮应该禁用
    await page.click('button:has-text("登录")');
    const loginButton = page.locator('button:has-text("登录")');
    await expect(loginButton).toBeDisabled();
  });

  test('密码输入框类型验证', async ({ page }) => {
    const passwordInput = page.locator('input[type="password"]');
    expect(await passwordInput.getAttribute('type')).toBe('password');
  });

  test('忘记密码链接', async ({ page }) => {
    await expect(page.locator('text=忘记密码？')).toBeVisible();
  });
});
