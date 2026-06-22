import { test, expect } from './fixtures';

test.describe('注册页面 - Register Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('页面元素完整性检查', async ({ page }) => {
    await expect(page.locator('text=QuantumTrader AI')).toBeVisible();
    await expect(page.locator('text=创建您的交易账户')).toBeVisible();
    await expect(page.locator('text=注册新账户')).toBeVisible();
    
    // 检查所有输入框
    await expect(page.locator('text=用户名')).toBeVisible();
    await expect(page.locator('text=邮箱地址')).toBeVisible();
    await expect(page.locator('text=密码')).toBeVisible();
    await expect(page.locator('text=确认密码')).toBeVisible();
    
    // 检查服务条款复选框
    await expect(page.locator('text=我已阅读并同意')).toBeVisible();
    await expect(page.locator('text=服务条款')).toBeVisible();
    await expect(page.locator('text=隐私政策')).toBeVisible();
    
    // 检查注册按钮
    await expect(page.locator('button:has-text("注册")')).toBeVisible();
    
    // 检查登录链接
    await expect(page.locator('text=已有账户？')).toBeVisible();
    await expect(page.locator('text=立即登录')).toBeVisible();
  });

  test('注册成功 - 正常流程', async ({ page }) => {
    await midscene(page, '在用户名输入框中输入 testuser123');
    await midscene(page, '在邮箱输入框中输入 newuser@example.com');
    await midscene(page, '在密码输入框中输入 Password123');
    await midscene(page, '在确认密码输入框中输入 Password123');
    await midscene(page, '勾选同意服务条款复选框');
    await midscene(page, '点击注册按钮');
    
    // 应该显示成功信息
    await expect(page.locator('text=注册成功')).toBeVisible({ timeout: 5000 });
  });

  test('两次密码不一致 - 异常流程', async ({ page }) => {
    await midscene(page, '用户名输入 testuser');
    await midscene(page, '邮箱输入 test@example.com');
    await midscene(page, '密码输入 Password123');
    await midscene(page, '确认密码输入 Different123');
    await midscene(page, '勾选同意服务条款');
    await midscene(page, '点击注册按钮');
    
    // 应该显示密码不一致错误
    await expect(page.locator('text=两次输入的密码不一致')).toBeVisible({ timeout: 3000 });
  });

  test('密码长度不足 - 边界情况', async ({ page }) => {
    await midscene(page, '用户名输入 testuser');
    await midscene(page, '邮箱输入 test@example.com');
    await midscene(page, '密码输入 1234567');
    await midscene(page, '确认密码输入 1234567');
    await midscene(page, '勾选同意服务条款');
    await midscene(page, '点击注册按钮');
    
    // 应该显示密码长度错误
    await expect(page.locator('text=密码长度至少为8位')).toBeVisible({ timeout: 3000 });
  });

  test('未勾选服务条款 - 异常流程', async ({ page }) => {
    await midscene(page, '用户名输入 testuser');
    await midscene(page, '邮箱输入 test@example.com');
    await midscene(page, '密码输入 Password123');
    await midscene(page, '确认密码输入 Password123');
    // 不勾选服务条款
    await midscene(page, '点击注册按钮');
    
    // HTML5 required验证应该阻止提交
    const checkbox = page.locator('input[type="checkbox"]').last();
    const isRequired = await checkbox.evaluate(el => el.required);
    expect(isRequired).toBeTruthy();
  });

  test('空用户名注册 - 边界情况', async ({ page }) => {
    await midscene(page, '邮箱输入 test@example.com');
    await midscene(page, '密码输入 Password123');
    await midscene(page, '确认密码输入 Password123');
    await midscene(page, '勾选同意服务条款');
    await midscene(page, '点击注册按钮');
    
    // 用户名应该是必填的
    const usernameInput = page.locator('input[type="text"]').first();
    const isRequired = await usernameInput.evaluate(el => el.required);
    expect(isRequired).toBeTruthy();
  });

  test('跳转到登录页面', async ({ page }) => {
    await midscene(page, '点击立即登录链接');
    await expect(page).toHaveURL('/login');
  });

  test('注册加载状态', async ({ page }) => {
    await midscene(page, '用户名输入 testuser');
    await midscene(page, '邮箱输入 test@example.com');
    await midscene(page, '密码输入 Password123');
    await midscene(page, '确认密码输入 Password123');
    await midscene(page, '勾选同意服务条款');
    await midscene(page, '点击注册按钮');
    
    // 按钮应该显示加载状态
    const registerButton = page.locator('button:has-text("注册")');
    await expect(registerButton).toBeDisabled();
  });

  test('密码输入框类型为password', async ({ page }) => {
    const passwordInput = page.locator('input[type="password"]').first();
    expect(await passwordInput.getAttribute('type')).toBe('password');
  });

  test('确认密码输入框类型为password', async ({ page }) => {
    const confirmInput = page.locator('input[type="password"]').nth(1);
    expect(await confirmInput.getAttribute('type')).toBe('password');
  });
});
