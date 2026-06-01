import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/ProjectOverview.vue'),
        meta: { title: '项目总览' }
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('../views/project/ProjectList.vue'),
        meta: { title: '项目管理' }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('../views/project/ProjectDetail.vue'),
        meta: { title: '项目详情' }
      },
      {
        path: 'testcases',
        name: 'TestCaseList',
        component: () => import('../views/testcase/TestCaseList.vue'),
        meta: { title: '测试用例' }
      },
      {
        path: 'reports',
        name: 'TestReportList',
        component: () => import('../views/report/TestReportList.vue'),
        meta: { title: '测试报告' }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('../views/knowledge/KnowledgeBase.vue'),
        meta: { title: '知识库' }
      },
      {
        path: 'knowledge/:id',
        name: 'KnowledgeDetail',
        component: () => import('../views/knowledge/KnowledgeDetail.vue'),
        meta: { title: '知识库详情' }
      },
      {
        path: 'knowledge/:id/folder/:folderId',
        name: 'KnowledgeDocs',
        component: () => import('../views/knowledge/KnowledgeDocs.vue'),
        meta: { title: '文档列表' }
      },
      {
        path: 'knowledge/graph',
        name: 'KnowledgeGraph',
        component: () => import('../views/knowledge/KnowledgeGraph.vue'),
        meta: { title: '知识图谱' }
      },
      {
        path: 'roles',
        name: 'RoleManagement',
        component: () => import('../views/role/RoleManagement.vue'),
        meta: { title: '角色管理' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/user/UserManagement.vue'),
        meta: { title: '用户管理' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
