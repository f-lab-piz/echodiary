import { test, expect } from '@playwright/test';

function uniqueUser() {
  const ts = Date.now().toString().slice(-8);
  return `e2e-user-${ts}`;
}

test('signup -> login -> chat -> generate diary -> verify content and image', async ({ page }) => {
  const username = uniqueUser();
  const password = 'pass1234';

  await page.goto('/signup');
  await page.getByPlaceholder('아이디').fill(username);
  await page.getByPlaceholder('비밀번호').fill(password);
  await page.getByRole('button', { name: '회원가입' }).click();
  await expect(page.getByText('회원가입 완료')).toBeVisible();

  await page.getByRole('button', { name: '로그인으로 이동' }).click();
  await page.getByPlaceholder('아이디').fill(username);
  await page.getByPlaceholder('비밀번호').fill(password);
  await page.getByRole('button', { name: '로그인' }).click();

  await expect
    .poll(async () => page.evaluate(() => !!localStorage.getItem('echodiary_token')), { timeout: 30000 })
    .toBe(true);

  // Nginx direct deep-link may 404 in current setup, so move through root route.
  await page.goto('/');

  await expect(page.getByRole('heading', { name: '오늘 하루는 어떠신가요' })).toBeVisible();

  const messageInput = page.getByPlaceholder('오늘 하루를 친구에게 말하듯 적어주세요');
  await messageInput.fill('오늘은 테스트 자동화를 진행했고 저녁에 산책을 했다.');
  await page.getByRole('button', { name: '메시지 보내기' }).click();

  await expect(page.getByText(/\[assistant\]/)).toBeVisible();

  await page.getByRole('button', { name: '대화 기반 일기 생성' }).click();
  await expect(page.getByText('요청 접수 완료. 백그라운드 생성이 시작되었습니다.')).toBeVisible();
  await expect(page.getByText('일기 생성 완료. 보관함에서 확인하세요.')).toBeVisible({ timeout: 180000 });

  await page.getByRole('button', { name: '일기 보관' }).click();
  await expect(page.getByRole('heading', { name: '일기 보관함' })).toBeVisible();

  const firstEntry = page.locator('.entry-card').first();
  await expect(firstEntry).toBeVisible({ timeout: 60000 });
  await expect(firstEntry.locator('.entry-text')).not.toBeEmpty();

  const image = firstEntry.locator('img.entry-image');
  await expect(image).toBeVisible({ timeout: 120000 });
  const src = await image.getAttribute('src');
  expect(src).toContain('blob:');
});
