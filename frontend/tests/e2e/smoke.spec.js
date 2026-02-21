import { expect, test } from "@playwright/test";

test("login -> open board -> open card -> start/stop timer", async ({ page }) => {
  const user = { id: 1, email: "demo@track.local" };
  const board = {
    id: 1,
    name: "Demo Board",
    color_hex: "#16A34A",
    description: "Smoke board",
    lists: [
      {
        id: 11,
        board_id: 1,
        title: "Todo",
        position: 0,
        cards: [
          {
            id: 101,
            list_id: 11,
            board_id: 1,
            title: "First task",
            description: "",
            position: 0,
            labels: [],
            checklists: [],
            images: [],
            total_tracked_seconds: 0,
          },
        ],
      },
    ],
    labels: [],
  };

  const cardDetails = {
    id: 101,
    list_id: 11,
    board_id: 1,
    title: "First task",
    description: "",
    labels: [],
    checklists: [],
    images: [],
    total_tracked_seconds: 0,
  };

  let activeSession = null;

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const method = request.method();
    const url = new URL(request.url());
    const path = url.pathname.replace(/^\/api(?:\/v1)?/, "");

    if (method === "POST" && path === "/auth/login") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "access-token", user }),
      });
      return;
    }

    if (method === "POST" && path === "/auth/refresh") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "access-token", user }),
      });
      return;
    }

    if (method === "GET" && path === "/auth/me") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(user),
      });
      return;
    }

    if (method === "GET" && path === "/boards") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([board]),
      });
      return;
    }

    if (method === "GET" && path === "/boards/1") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(board),
      });
      return;
    }

    if (method === "GET" && path === "/boards/1/labels") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
      return;
    }

    if (method === "GET" && path === "/cards/101") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(cardDetails),
      });
      return;
    }

    if (method === "GET" && path === "/cards/101/time") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_seconds: activeSession ? 1 : 0,
        }),
      });
      return;
    }

    if (method === "GET" && path === "/users/me/active-timer") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ active_session: activeSession }),
      });
      return;
    }

    if (method === "POST" && path === "/cards/101/timer/start") {
      activeSession = {
        id: 9001,
        card_id: 101,
        user_id: 1,
        started_at: new Date().toISOString(),
        ended_at: null,
      };
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          session: activeSession,
          summary: { total_seconds: 0 },
        }),
      });
      return;
    }

    if (method === "POST" && path === "/cards/101/timer/stop") {
      activeSession = null;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          summary: { total_seconds: 3 },
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({}),
    });
  });

  await page.goto("/login");
  await page.getByLabel("Email").fill("demo@track.local");
  await page.getByLabel("Password").fill("secret");
  await page.getByRole("button", { name: "Log in" }).click();

  await expect(page.getByText("Your Boards")).toBeVisible();
  await page.getByText("Demo Board").first().click();
  await expect(page.getByText("First task")).toBeVisible();

  await page.getByText("First task").first().click();
  await expect(page.getByText("Delete card")).toBeVisible();

  await page.getByRole("button", { name: "Start" }).click();
  await expect(page.getByText("Running since")).toBeVisible();

  await page.reload();
  await page.getByText("First task").first().click();
  await expect(page.getByText("Running since")).toBeVisible();

  await page.getByRole("button", { name: "Stop" }).click();
  await expect(page.getByText("Total tracked")).toBeVisible();
});
