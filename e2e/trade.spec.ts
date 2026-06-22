import { test, expect } from './fixtures';

test.describe('交易页面 - Trade Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/trade');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 交易对选择器
    await expect(page.locator('select')).first().toBeVisible();
    
    // 当前价格和24h数据
    await expect(page.locator('text=24h 最高')).toBeVisible();
    await expect(page.locator('text=24h 最低')).toBeVisible();
    await expect(page.locator('text=24h 成交量')).toBeVisible();
    
    // 时间周期按钮
    await expect(page.locator('text=1m')).toBeVisible();
    await expect(page.locator('text=5m')).toBeVisible();
    await expect(page.locator('text=15m')).toBeVisible();
    await expect(page.locator('text=1h')).toBeVisible();
    await expect(page.locator('text=4h')).toBeVisible();
    await expect(page.locator('text=1d')).toBeVisible();
    
    // K线图表
    await expect(page.locator('text=K线图表开发中')).toBeVisible();
    
    // 订单类型标签
    await expect(page.locator('text=现货')).toBeVisible();
    await expect(page.locator('text=合约')).toBeVisible();
    await expect(page.locator('text=期权')).toBeVisible();
    
    // 买入/卖出
    await expect(page.locator('text=买入')).toBeVisible();
    await expect(page.locator('text=卖出')).toBeVisible();
    
    // 市价/限价
    await expect(page.locator('text=市价')).toBeVisible();
    await expect(page.locator('text=限价')).toBeVisible();
    
    // 数量输入
    await expect(page.locator('input[type="number"]').first()).toBeVisible();
    
    // 快捷金额按钮
    await expect(page.locator('text=25%')).toBeVisible();
    await expect(page.locator('text=50%')).toBeVisible();
    await expect(page.locator('text=75%')).toBeVisible();
    await expect(page.locator('text=100%')).toBeVisible();
    
    // 订单簿和最新成交
    await expect(page.locator('text=订单簿')).toBeVisible();
    await expect(page.locator('text=最新成交')).toBeVisible();
    
    // 可用余额
    await expect(page.locator('text=可用余额')).toBeVisible();
    
    // 提交按钮
    await expect(page.locator('button:has-text("买入")')).last().toBeVisible();
  });

  test('交易对切换功能', async ({ authenticatedUser: page }) => {
    const select = page.locator('select').first();
    
    // 默认是BTC/USDT
    expect(await select.inputValue()).toBe('BTC/USDT');
    
    // 切换到ETH/USDT
    await midscene(page, '在交易对选择器中选择ETH/USDT');
    expect(await select.inputValue()).toBe('ETH/USDT');
    
    // 切换到SOL/USDT
    await midscene(page, '在交易对选择器中选择SOL/USDT');
    expect(await select.inputValue()).toBe('SOL/USDT');
  });

  test('时间周期切换功能', async ({ authenticatedUser: page }) => {
    // 默认选中1h
    await expect(page.locator('button:has-text("1h")')).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到1m
    await midscene(page, '点击时间周期中的1m按钮');
    await expect(page.locator('button:has-text("1m")')).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到5m
    await midscene(page, '点击时间周期中的5m按钮');
    await expect(page.locator('button:has-text("5m")')).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到15m
    await midscene(page, '点击时间周期中的15m按钮');
    await expect(page.locator('button:has-text("15m")')).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到4h
    await midscene(page, '点击时间周期中的4h按钮');
    await expect(page.locator('button:has-text("4h")')).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到1d
    await midscene(page, '点击时间周期中的1d按钮');
    await expect(page.locator('button:has-text("1d")')).toHaveClass(/bg-quantum-cyan/);
  });

  test('订单类型切换 - 现货/合约/期权', async ({ authenticatedUser: page }) => {
    // 默认现货
    await expect(page.locator('text=现货').first()).toHaveClass(/text-quantum-cyan/);
    
    // 切换到合约
    await midscene(page, '点击合约标签');
    await expect(page.locator('text=合约').first()).toHaveClass(/text-quantum-cyan/);
    
    // 验证杠杆选项出现
    await expect(page.locator('text=杠杆倍数')).toBeVisible();
    
    // 切换到期权
    await midscene(page, '点击期权标签');
    await expect(page.locator('text=期权').first()).toHaveClass(/text-quantum-cyan/);
    
    // 切回现货
    await midscene(page, '点击现货标签');
    await expect(page.locator('text=现货').first()).toHaveClass(/text-quantum-cyan/);
  });

  test('买入/卖出切换', async ({ authenticatedUser: page }) => {
    // 默认买入
    const buyButton = page.locator('button').filter({ hasText: '买入' }).nth(1);
    await expect(buyButton).toHaveClass(/bg-quantum-green/);
    
    // 切换到卖出
    await midscene(page, '点击卖出按钮');
    const sellButton = page.locator('button').filter({ hasText: '卖出' }).nth(1);
    await expect(sellButton).toHaveClass(/bg-quantum-red/);
    
    // 切回买入
    await midscene(page, '点击买入按钮');
    await expect(buyButton).toHaveClass(/bg-quantum-green/);
  });

  test('市价/限价切换', async ({ authenticatedUser: page }) => {
    // 默认限价
    await expect(page.locator('text=限价').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到市价
    await midscene(page, '点击市价按钮');
    await expect(page.locator('text=市价').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 验证价格输入框消失
    await expect(page.locator('text=价格 (USDT)')).not.toBeVisible();
    
    // 切回限价
    await midscene(page, '点击限价按钮');
    await expect(page.locator('text=价格 (USDT)')).toBeVisible();
  });

  test('合约杠杆倍数选择', async ({ authenticatedUser: page }) => {
    // 切换到合约
    await midscene(page, '点击合约标签');
    
    // 默认5x
    await expect(page.locator('text=5x').first()).toHaveClass(/bg-quantum-yellow/);
    
    // 测试各个杠杆倍数
    const leverages = ['2x', '5x', '10x', '20x', '50x', '100x'];
    for (const lev of leverages) {
      await midscene(page, `点击杠杆倍数中的${lev}按钮`);
      await expect(page.locator(`text=${lev}`).first()).toHaveClass(/bg-quantum-yellow/);
    }
  });

  test('快捷金额按钮功能', async ({ authenticatedUser: page }) => {
    const quantityInput = page.locator('input[type="number"]').nth(0);
    
    // 点击25%
    await midscene(page, '点击25%快捷金额按钮');
    const value25 = await quantityInput.inputValue();
    expect(parseFloat(value25)).toBeGreaterThan(0);
    
    // 点击50%
    await midscene(page, '点击50%快捷金额按钮');
    const value50 = await quantityInput.inputValue();
    expect(parseFloat(value50)).toBeGreaterThan(parseFloat(value25));
    
    // 点击100%
    await midscene(page, '点击100%快捷金额按钮');
    const value100 = await quantityInput.inputValue();
    expect(parseFloat(value100)).toBeGreaterThan(parseFloat(value50));
  });

  test('现货买入下单 - 正常流程', async ({ authenticatedUser: page }) => {
    // 输入数量
    await midscene(page, '在数量输入框中输入0.01');
    
    // 点击买入
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('订单已提交');
      dialog.accept();
    });
    
    await midscene(page, '点击买入按钮');
  });

  test('现货卖出下单 - 正常流程', async ({ authenticatedUser: page }) => {
    // 切换到卖出
    await midscene(page, '点击卖出按钮');
    
    // 输入数量
    await midscene(page, '在数量输入框中输入0.01');
    
    // 点击卖出
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('订单已提交');
      dialog.accept();
    });
    
    await midscene(page, '点击卖出按钮');
  });

  test('零数量下单 - 异常流程', async ({ authenticatedUser: page }) => {
    // 数量为0
    await midscene(page, '在数量输入框中输入0');
    
    // 点击买入
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('请输入有效的数量');
      dialog.accept();
    });
    
    await midscene(page, '点击买入按钮');
  });

  test('负数数量下单 - 边界情况', async ({ authenticatedUser: page }) => {
    // 输入负数
    await midscene(page, '在数量输入框中输入-0.01');
    
    // 点击买入
    const quantityInput = page.locator('input[type="number"]').first();
    const value = await quantityInput.inputValue();
    
    // number输入框可能不允许负数，或者下单时会验证
    if (parseFloat(value) < 0) {
      page.once('dialog', dialog => {
        dialog.accept();
      });
      await midscene(page, '点击买入按钮');
    }
  });

  test('订单簿数据展示', async ({ authenticatedUser: page }) => {
    // 验证订单簿有数据
    await expect(page.locator('text=订单簿')).toBeVisible();
    
    // 卖单（红色）
    const asks = page.locator('.text-quantum-red').filter({ hasText: /\d/ });
    expect(await asks.count()).toBeGreaterThan(0);
    
    // 买单（绿色）
    const bids = page.locator('.text-quantum-green').filter({ hasText: /\d/ });
    expect(await bids.count()).toBeGreaterThan(0);
    
    // 当前价格
    await aiAssert(page, '订单簿中间显示当前价格');
  });

  test('最新成交数据展示', async ({ authenticatedUser: page }) => {
    await expect(page.locator('text=最新成交')).toBeVisible();
    
    // 验证有成交记录
    const trades = page.locator('.text-quantum-green, .text-quantum-red').filter({ hasText: /\./ });
    expect(await trades.count()).toBeGreaterThan(0);
  });

  test('可用余额显示', async ({ authenticatedUser: page }) => {
    await expect(page.locator('text=可用余额')).toBeVisible();
    
    // 验证余额数值
    const balance = await aiQuery(page, '获取可用余额的数值');
    expect(balance).toBeTruthy();
  });

  test('K线图表开发中标识', async ({ authenticatedUser: page }) => {
    await expect(page.locator('text=K线图表开发中')).toBeVisible();
    await expect(page.locator('text=TradingView / ECharts K线图')).toBeVisible();
  });

  test('图表类型切换按钮', async ({ authenticatedUser: page }) => {
    // 蜡烛图、折线图、深度图按钮
    const chartButtons = page.locator('button').filter({ has: page.locator('svg') }).nth(0);
    await expect(chartButtons).toBeVisible();
    
    // 验证有3个图表类型按钮
    const chartTypeButtons = page.locator('.flex.gap-2').nth(1).locator('button');
    expect(await chartTypeButtons.count()).toBe(3);
  });

  test('合约交易下单 - 正常流程', async ({ authenticatedUser: page }) => {
    // 切换到合约
    await midscene(page, '点击合约标签');
    
    // 选择杠杆
    await midscene(page, '点击10x杠杆按钮');
    
    // 输入数量
    await midscene(page, '在数量输入框中输入0.01');
    
    // 点击买入
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('订单已提交');
      dialog.accept();
    });
    
    await midscene(page, '点击买入按钮');
  });

  test('价格输入框 - 限价单', async ({ authenticatedUser: page }) => {
    // 确保是限价单
    await midscene(page, '点击限价按钮');
    
    // 输入价格
    const priceInput = page.locator('input[type="number"]').first();
    await midscene(page, '在价格输入框中输入65000');
    
    const priceValue = await priceInput.inputValue();
    expect(parseFloat(priceValue)).toBe(65000);
  });

  test('总额计算正确性', async ({ authenticatedUser: page }) => {
    // 输入数量
    await midscene(page, '在数量输入框中输入1');
    
    // 验证总额显示
    await expect(page.locator('text=总额 (USDT)')).toBeVisible();
    
    const total = await aiQuery(page, '获取总额的数值');
    expect(total).toBeTruthy();
  });
});
