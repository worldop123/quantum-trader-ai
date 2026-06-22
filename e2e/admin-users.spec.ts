import { test, expect } from './fixtures';

test.describe('管理后台 - 用户管理', () => {
  test.beforeEach(async ({ authenticatedAdmin: page }) => {
    await page.goto('/admin/users');
  });

  test('页面元素完整性检查', async ({ authenticatedAdmin: page }) => {
    // 搜索框
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    
    // 筛选器
    await expect(page.locator('select').first()).toBeVisible();
    
    // 添加用户按钮
    await expect(page.locator('text=添加用户')).toBeVisible();
    
    // 表格列
    await expect(page.locator('text=用户ID')).toBeVisible();
    await expect(page.locator('text=用户名')).toBeVisible();
    await expect(page.locator('text=邮箱')).toBeVisible();
    await expect(page.locator('text=角色')).toBeVisible();
    await expect(page.locator('text=总资产')).toBeVisible();
    await expect(page.locator('text=状态')).toBeVisible();
    await expect(page.locator('text=注册时间')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
  });

  test('搜索用户功能', async ({ authenticatedAdmin: page }) => {
    const searchInput = page.locator('input[type="text"]').first();
    
    // 输入搜索内容
    await midscene(page, '在搜索框中输入test');
    const value = await searchInput.inputValue();
    expect(value).toContain('test');
  });

  test('状态筛选功能', async ({ authenticatedAdmin: page }) => {
    const select = page.locator('select').first();
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在状态筛选中选择已禁用');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('角色筛选功能', async ({ authenticatedAdmin: page }) => {
    const select = page.locator('select').nth(1);
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在角色筛选中选择管理员');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('用户表格数据展示', async ({ authenticatedAdmin: page }) => {
    // 验证有用户数据
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
    
    // 验证用户信息
    await aiAssert(page, '用户表格中显示了用户ID、用户名、邮箱等信息');
  });

  test('添加用户功能', async ({ authenticatedAdmin: page }) => {
    // 点击添加用户
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('添加');
      dialog.accept();
    });
    
    await midscene(page, '点击添加用户按钮');
  });

  test('查看用户详情功能', async ({ authenticatedAdmin: page }) => {
    // 点击查看
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('查看');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个用户的查看按钮');
  });

  test('编辑用户功能', async ({ authenticatedAdmin: page }) => {
    // 点击编辑
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('编辑');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个用户的编辑按钮');
  });

  test('禁用用户功能', async ({ authenticatedAdmin: page }) => {
    // 点击禁用
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('禁用');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个用户的禁用按钮');
  });

  test('用户状态颜色标识', async ({ authenticatedAdmin: page }) => {
    // 验证状态有颜色标识
    await aiAssert(page, '用户表格中不同状态的用户有不同的颜色标识');
  });

  test('分页功能', async ({ authenticatedAdmin: page }) => {
    // 检查分页元素
    await expect(page.locator('text=上一页')).toBeVisible();
    await expect(page.locator('text=下一页')).toBeVisible();
  });

  test('用户角色显示', async ({ authenticatedAdmin: page }) => {
    // 验证有角色列
    await expect(page.locator('text=角色')).toBeVisible();
    
    // 验证显示用户角色
    await aiAssert(page, '用户表格中显示了用户角色，如普通用户或管理员');
  });
});
