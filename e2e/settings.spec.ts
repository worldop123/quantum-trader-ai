import { test, expect } from './fixtures';

test.describe('设置页面 - Settings Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/settings');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 侧边栏导航
    await expect(page.locator('text=个人信息')).toBeVisible();
    await expect(page.locator('text=安全设置')).toBeVisible();
    await expect(page.locator('text=API管理')).toBeVisible();
    await expect(page.locator('text=偏好设置')).toBeVisible();
    await expect(page.locator('text=关于我们')).toBeVisible();
  });

  test('个人信息页面展示', async ({ authenticatedUser: page }) => {
    // 默认显示个人信息
    await expect(page.locator('text=个人信息')).toBeVisible();
    await expect(page.locator('text=用户名')).toBeVisible();
    await expect(page.locator('text=邮箱')).toBeVisible();
    await expect(page.locator('text=手机号')).toBeVisible();
    await expect(page.locator('text=国家/地区')).toBeVisible();
    
    // 邮箱不可修改
    const emailInput = page.locator('input[type="email"]').first();
    expect(await emailInput.isDisabled()).toBeTruthy();
  });

  test('个人信息编辑功能', async ({ authenticatedUser: page }) => {
    // 修改用户名
    const usernameInput = page.locator('input[type="text"]').first();
    await midscene(page, '在用户名输入框中输入testuser_new');
    expect(await usernameInput.inputValue()).toContain('testuser_new');
    
    // 修改手机号
    const phoneInput = page.locator('input[type="tel"]').first();
    await midscene(page, '在手机号输入框中输入13800138000');
    expect(await phoneInput.inputValue()).toBe('13800138000');
    
    // 保存修改
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('保存');
      dialog.accept();
    });
    
    await midscene(page, '点击保存按钮');
  });

  test('头像上传功能', async ({ authenticatedUser: page }) => {
    // 验证有头像区域
    await expect(page.locator('text=头像')).toBeVisible();
    
    // 点击上传头像
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('上传');
      dialog.accept();
    });
    
    await midscene(page, '点击头像上传按钮');
  });

  test('安全设置页面', async ({ authenticatedUser: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    // 验证安全设置项
    await expect(page.locator('text=登录密码')).toBeVisible();
    await expect(page.locator('text=资金密码')).toBeVisible();
    await expect(page.locator('text=双重验证')).toBeVisible();
    await expect(page.locator('text=登录设备管理')).toBeVisible();
  });

  test('修改登录密码功能', async ({ authenticatedUser: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    // 点击修改密码
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('密码');
      dialog.accept();
    });
    
    await midscene(page, '点击登录密码的修改按钮');
  });

  test('双重验证开关', async ({ authenticatedUser: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    // 双重验证开关
    const twoFaSwitch = page.locator('input[type="checkbox"]').nth(0);
    await midscene(page, '点击双重验证开关');
    expect(await twoFaSwitch.isChecked()).toBeTruthy();
  });

  test('API管理页面', async ({ authenticatedUser: page }) => {
    // 切换到API管理
    await midscene(page, '点击侧边栏中的API管理');
    
    // 验证API Key列表
    await expect(page.locator('text=API Key')).toBeVisible();
    await expect(page.locator('text=创建API')).toBeVisible();
  });

  test('创建API Key功能', async ({ authenticatedUser: page }) => {
    // 切换到API管理
    await midscene(page, '点击侧边栏中的API管理');
    
    // 点击创建API
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('创建');
      dialog.accept();
    });
    
    await midscene(page, '点击创建API按钮');
  });

  test('偏好设置页面', async ({ authenticatedUser: page }) => {
    // 切换到偏好设置
    await midscene(page, '点击侧边栏中的偏好设置');
    
    // 验证偏好设置项
    await expect(page.locator('text=界面语言')).toBeVisible();
    await expect(page.locator('text=主题模式')).toBeVisible();
    await expect(page.locator('text=价格小数位')).toBeVisible();
    await expect(page.locator('text=交易确认')).toBeVisible();
  });

  test('界面语言切换', async ({ authenticatedUser: page }) => {
    // 切换到偏好设置
    await midscene(page, '点击侧边栏中的偏好设置');
    
    // 切换语言
    const langSelect = page.locator('select').first();
    await midscene(page, '在界面语言选择器中选择English');
    expect(await langSelect.inputValue()).toBeTruthy();
  });

  test('主题模式切换', async ({ authenticatedUser: page }) => {
    // 切换到偏好设置
    await midscene(page, '点击侧边栏中的偏好设置');
    
    // 主题模式开关
    const themeSwitch = page.locator('input[type="checkbox"]').nth(0);
    await midscene(page, '点击主题模式开关');
    expect(await themeSwitch.isChecked()).toBeTruthy();
  });

  test('价格小数位设置', async ({ authenticatedUser: page }) => {
    // 切换到偏好设置
    await midscene(page, '点击侧边栏中的偏好设置');
    
    // 设置小数位
    const decimalSelect = page.locator('select').nth(1);
    await midscene(page, '在价格小数位选择器中选择4位');
    expect(await decimalSelect.inputValue()).toBeTruthy();
  });

  test('交易确认开关', async ({ authenticatedUser: page }) => {
    // 切换到偏好设置
    await midscene(page, '点击侧边栏中的偏好设置');
    
    // 交易确认开关
    const confirmSwitch = page.locator('input[type="checkbox"]').nth(1);
    await midscene(page, '点击交易确认开关');
    expect(await confirmSwitch.isChecked()).toBeTruthy();
  });

  test('关于我们页面', async ({ authenticatedUser: page }) => {
    // 切换到关于我们
    await midscene(page, '点击侧边栏中的关于我们');
    
    // 验证系统信息
    await expect(page.locator('text=版本')).toBeVisible();
    await expect(page.locator('text=构建时间')).toBeVisible();
    await expect(page.locator('text=技术支持')).toBeVisible();
    await expect(page.locator('text=服务条款')).toBeVisible();
    await expect(page.locator('text=隐私政策')).toBeVisible();
    await expect(page.locator('text=风险提示')).toBeVisible();
  });

  test('服务条款链接', async ({ authenticatedUser: page }) => {
    // 切换到关于我们
    await midscene(page, '点击侧边栏中的关于我们');
    
    // 点击服务条款
    page.once('dialog', dialog => {
      dialog.accept();
    });
    
    await midscene(page, '点击服务条款链接');
  });

  test('隐私政策链接', async ({ authenticatedUser: page }) => {
    // 切换到关于我们
    await midscene(page, '点击侧边栏中的关于我们');
    
    // 点击隐私政策
    page.once('dialog', dialog => {
      dialog.accept();
    });
    
    await midscene(page, '点击隐私政策链接');
  });

  test('侧边栏导航切换', async ({ authenticatedUser: page }) => {
    // 测试所有导航项
    const navItems = ['个人信息', '安全设置', 'API管理', '偏好设置', '关于我们'];
    
    for (const item of navItems) {
      await midscene(page, `点击侧边栏中的${item}`);
      await expect(page.locator(`text=${item}`).first()).toHaveClass(/text-quantum-cyan/);
    }
  });
});
