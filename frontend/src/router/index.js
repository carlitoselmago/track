import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import LoginView from "@/views/LoginView.vue";
import BoardListView from "@/views/BoardListView.vue";
import KanbanBoardView from "@/views/KanbanBoardView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: "/",
      redirect: "/boards",
    },
    {
      path: "/",
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: "boards",
          name: "boards",
          component: BoardListView,
        },
        {
          path: "boards/:boardId",
          name: "board",
          component: KanbanBoardView,
          props: true,
        },
      ],
    },
  ],
});

export default router;
