var gitalkConfig = {
  clientID: '\x66\x64\x62\x65\x66\x36\x33\x64\x65\x33\x39\x32\x30\x65\x64\x36\x36\x32\x61\x61',
  clientSecret:
    '\x38\x63\x31\x62\x38\x62\x32\x34\x39\x39\x34\x32\x34\x35\x39\x35\x64\x39\x36\x65\x35\x61\x35\x38\x33\x32\x36\x39\x63\x39\x66\x33\x63\x30\x32\x37\x66\x62\x30\x66',
  language: '\x7a\x68\x2d\x43\x4e',
  repo: '\x64\x6f\x63\x73',
  owner: '\x78\x66\x6c\x69\x68\x61\x69\x62\x6f',
  githubID: '\x78\x66\x6c\x69\x68\x61\x69\x62\x6f',
  id: location['\x70\x61\x74\x68\x6e\x61\x6d\x65'],
  perPage: 20,
  admin: ['\x78\x66\x6c\x69\x68\x61\x69\x62\x6f'],
  distractionFreeMode: false
};

window.$docsify = {
  el: '#app',
  themeColor: '#39BAE8',
  name: '📖   杜泽杰的博客',
  // logo: './config/img/xfshz.PNG',
  auto2top: true, //切换页面后是否自动跳转到页面顶部
  maxLevel: 6, //配置最大支持渲染的标题层级
  onlyCover: false, // 主页仅加载封面，不能滚动到其他页
  //页面设置
  loadSidebar: true, //加载自定义侧边栏
  // loadSidebar: 'config/_sidebar.md',
  loadNavbar: true, //加载自定义导航栏
  // loadNavbar: 'config/_navbar.md',
  // coverpage: true, //封面图
  coverpage: 'config/_coverpage.md',
  subMaxLevel: 2,   // sidebar 展示md TOC层级
  notFoundPage: 'config/error.md',
  mergeNavbar: true, // Navbar将在较小的屏幕上与侧边栏合并
  // routerMode: 'history', //路由方式 默认hash
  // basePath: '/duzejie/',
  // nameLink: '/docs/',
  //relativePath: false,
  subMaxLevel: 2, //自定义侧边栏同时也可以开启目录功能
  // repo: 'https://github.com/xflihaibo/docs', // 右上角小部件
  formatUpdated: '{YYYY}-{MM}-{DD} {HH}:{mm}', //变量显示文档更新日期
  // count: {
  //   countable: true,
  //   fontsize: '0.9em',
  //   color: 'rgb(90,90,90)',
  //   language: 'chinese',
  //   float: "left"
  // },
  alias: {
    '/_sidebar.md': '/config/_sidebar.md', // See #301
    '/_navbar.md': '/config/_navbar.md',
  },
  search: {
    placeholder: '  🔍  搜索试试',
    noData: '抱歉！找不到对应的结果',
    depth: 6
  },
  pagination: {
    previousText: '上一节',
    nextText: '下一节',
    crossChapter: true
  },
  copyCode: {
    buttonText: '点击复制',
    errorText: '错误',
    successText: '复制成功'
  },
  footer: {
    copy: '<span>Navyum &copy; 2025</span>',
    // auth: '赣ICP备2024',
    auth: '好好学习天天向上',
    pre: '<hr/>',
    style: 'text-align: right;',
    class: 'className'
  },

  markdown: {             //drawio支持
    renderer: {
      code: function (code, lang) {
        if (lang === 'drawio') {
          if (window.drawioConverter) {
            console.log('drawio 转化中')
            return window.drawioConverter(code)
          } else {
            return `<div class='drawio-code'>${code}</div>`
          }
        } else {
          return this.origin.code.apply(this, arguments);
        }
      }
    }
  },


  plugins: [
    // DocsifyCodefund.create('xxxx-xxx-xxx'), // change to your codefund id
    function (hook, vm) {
      hook.beforeEach(function (html) {
        return html + '\n' + '⏰ 更新于： {docsify-updated} ';
      });

      hook.doneEach(function () {
        var label, domObj, main, divEle, gitalk;
        label = vm.route.path.split('/').pop();
        domObj = Docsify.dom;
        main = domObj.getNode('#main');
        Array.apply(null, document.querySelectorAll('div.gitalk-container')).forEach(function (ele) {
          ele.remove();
        });
        divEle = domObj.create('div');
        divEle.id = 'gitalk-container-' + label;
        divEle.className = 'gitalk-container';
        divEle.style = 'width: ' + main.clientWidth + 'px; margin: 0 auto 20px;';
        domObj.appendTo(domObj.find('.content'), divEle);
        gitalk = new Gitalk(Object.assign(gitalkConfig, { id: !label ? 'home' : label }));
        gitalk.render('gitalk-container-' + label);
      });
    }
  ]
};
