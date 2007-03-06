/******************************************************************************\
 from YUI                                                                     */

var ua = navigator.userAgent.toLowerCase();
var isOpera = (ua.indexOf('opera') > -1);
var isSafari = (ua.indexOf('safari') > -1);
var isIE = (window.ActiveXObject);

Doc = { // represent the document

  getHeight: function() {
    /*Return the height of the document.

      @return {Int}   The height of the actual document (which includes the
                      body and its margin).

    */
    var scrollHeight=-1,windowHeight=-1,bodyHeight=-1;
    var marginTop = computedStyle(document.body, 'marginTop');
        marginTop = marginTop ? parseInt(marginTop, 10) : 0;
    var marginBottom = computedStyle(document.body, 'marginBottom');
        marginBottom = marginBottom ? parseInt(marginBottom, 10) : 0;

    var mode = document.compatMode;

    if ( (mode || isIE) && !isOpera ) { // (IE, Gecko)
      switch (mode) {
        case 'CSS1Compat': // Standards mode
          scrollHeight = ((window.innerHeight && window.scrollMaxY) ?  window.innerHeight+window.scrollMaxY : -1);
          windowHeight = [document.documentElement.clientHeight,self.innerHeight||-1].sort(function(a, b){return(a-b);})[1];
          bodyHeight = document.body.offsetHeight + marginTop + marginBottom;
          break;

        default: // Quirks
          scrollHeight = document.body.scrollHeight;
          bodyHeight = document.body.clientHeight;
      }
    } else { // Safari & Opera
      scrollHeight = document.documentElement.scrollHeight;
      windowHeight = self.innerHeight;
      bodyHeight = document.documentElement.clientHeight;
    }

    var h = [scrollHeight,windowHeight,bodyHeight].sort(function(a, b){return(a-b);});
    return h[2];

  },

  getWidth: function() {
    /* Return the width of the document.

      @return {Int}   The width of the actual document (which includes the body
                      and its margin).

    */
    var docWidth=-1,bodyWidth=-1,winWidth=-1;
    var marginRight = parseInt(computedStyle(document.body, 'marginRight'), 10);
    var marginLeft = parseInt(computedStyle(document.body, 'marginLeft'), 10);

    var mode = document.compatMode;

    if (mode || isIE) { // (IE, Gecko, Opera)
      switch (mode) {
        case 'CSS1Compat': // Standards mode
          docWidth = document.documentElement.clientWidth;
          bodyWidth = document.body.offsetWidth + marginLeft + marginRight;
          winWidth = self.innerWidth || -1;
          break;

        default: // Quirks
          bodyWidth = document.body.clientWidth;
          winWidth = document.body.scrollWidth;
          break;
      }
    } else { // Safari
      docWidth = document.documentElement.clientWidth;
      bodyWidth = document.body.offsetWidth + marginLeft + marginRight;
      winWidth = self.innerWidth;
    }

    var w = [docWidth,bodyWidth,winWidth].sort(function(a, b){return(a-b);});
    return w[2];
  }
};

/* end YUI
\******************************************************************************/


// Set up some global HTML artifacts.
// ==================================

var zetaGreen = '#00A251';
var black = '#000000';

Mask = {
  // Represent the modal mask between Overlight and the site itself.

  mask: null,
  bgcolor: zetaGreen, // #439539
  opacity: 0.67, // 0.95,

  style: 'position: absolute; z-index: 998;',

  toString:function() {
    return 'Overlight Mask';
  },

  create: function() {
    css = this.style + 'background:' + this.bgcolor + ';';
    this.mask = DIV({id:'overlight-mask',style:css});
    setOpacity(this.mask, this.opacity);
    this.resize();
  },

  turn_on: function() {
    this.create();
    appendChildNodes(currentDocument().body, this.mask);
  },

  turn_off: function() {
    var mask = $('overlight-mask');
    if (mask) { removeElement(mask); }
  },

  resize: function() {
    if (this.mask) { // always true after the first time

      dim = {}
      dim.w = Doc.getWidth();
      dim.h = Doc.getHeight();

      pos = {x:0, y:0};

      setElementDimensions(this.mask, dim);
      setElementPosition(this.mask, pos);
    }
  }

};
connect(window, 'onresize', Mask, Mask.resize);


Ready = {
  // Represent the border in the ready state.

  ready: null,

  style: 'color: #00A251; font: bold 140px Arial, sans-serif; position: absolute; z-index: 1000;',
    // #439539
    // #00A251

  toString:function() {
    return 'Overlight Ready';
  },

  create: function() {
    this.ready = DIV({id:'overlight-ready',style:this.style},'Ready');
    setOpacity(this.ready, 0.33);
    this.reposition();
  },

  turn_on: function() {
    if (!this.ready) { this.create(); } // only true the first time
    appendChildNodes(currentDocument().body, this.ready);
  },

  turn_off: function() {
    var ready = $('overlight-ready');
    if (ready) { removeElement(ready); }
  },

  reposition: function() {
    if (this.ready) { // always true after the first time

      pos = {}
      pos.x = document.documentElement.scrollLeft + 10;
      pos.y = document.documentElement.scrollTop + getViewportDimensions().h - 180;

      setElementPosition(this.ready, pos);
    }
  }

};
connect(window, 'onresize', Ready, Ready.reposition);
connect(window, 'onscroll', Ready, Ready.reposition);


Overlight = {
  // Represent the sandbox for Overlight UI.

  overlight: null,  // the div
  dim: null,        // the width and height of the div

  style: 'background: white; position: absolute; z-index: 999; border: 2px solid black;',

  toString:function() {
    return 'Overlight';
  },

  create: function() {
    this.overlight = DIV({id:'overlight', style:this.style});
    //setOpacity(...); // In IE, this conflicts with any effects in the iframe.
    this.resize();
  },

  destroy: function() {
    var overlight = $('overlight');
    if (overlight) {
      removeElement(this.overlight);
    }
    this.overlight = null;
  },

  recreate: function() {
    this.destroy();
    this.create();
  },

  show: function() {
    appendChildNodes(currentDocument().body, this.overlight);
  },

  resize: function() {

    if (this.overlight) {

      // Dimensions: Default to Viewport - 100px
      // =======================================

      var dim = this.getDimensions();
      setElementDimensions(this.overlight, dim);
      this.reposition();

    }

  },

  reposition: function() {

    if (this.overlight) {

      // Position: Center It
      // ===================

      var dim = this.getDimensions();
      var viewport = getViewportDimensions();

      offset_ = {};
      offset_.x = document.documentElement.scrollLeft;
      offset_.y = document.documentElement.scrollTop;

      var pos = {}
      pos.x = offset_.x + Math.floor((viewport.w - this.dim.w) / 2);
      pos.y = offset_.y + Math.floor((viewport.h - this.dim.h) / 2);
      setElementPosition(this.overlight, pos);
      this.pos = pos;

    }

  },

  getDimensions: function() {
    if (!this.dim) {
      var viewport = getViewportDimensions();
      var dim = {};
      dim.w = viewport.w - 100;
      dim.h = viewport.h - 100;
      if (dim.w < 0) { dim.w = 0; }
      if (dim.h < 0) { dim.h = 0; }
      this.dim = dim;
    }
    return this.dim;
  }

};
connect(window, 'onresize', Overlight, Overlight.resize);
connect(window, 'onscroll', Overlight, Overlight.reposition);


// Close
// =====

Close = {
  // Represent the modal dialog's close button.

  style: 'cursor: pointer; position: absolute; z-index: 1000;',

  toString:function() {
    return 'Close Button';
  },

  turn_on: function() {
    var knob= IMG({ src:'_lib/close.gif'
                  , id:'overlight-close'
                  , style:this.style
                   });

    connect(knob, 'onmouseover',
      function() {
        knob.src = '_lib/close-on.gif'
      });
    connect(knob, 'onmouseout',
      function() {
        knob.src = '_lib/close.gif'
      });
    connect(knob, 'onclick',
      function() {
        states.default_.enter();
      });

    appendChildNodes(currentDocument().body, knob);
    this.knob = knob;
    this.resize();

  },

  turn_off: function() {
    var knob = $('overlight-close');
    if (knob) {
      removeElement(knob);
    }
  },

  resize: function() {
    this.reposition();
  },

  reposition: function() {
    if (this.knob) {
      var pos = {};
      pos.x = Overlight.pos.x + Overlight.dim.w - 118;
      pos.y = Overlight.pos.y - 23;
      setElementPosition(this.knob, pos);
    }
  }

};
connect(window, 'onresize', Close, Close.resize);
connect(window, 'onscroll', Close, Close.reposition);


// Loading
// =======

Loading = {
  // Represent the modal dialog's 'Loading...' spinner.

  style: 'position: absolute; z-index: 1000',

  toString:function() {
    return 'Loading Indicator';
  },

  turn_on: function() {
    var knob= IMG({ src:'_lib/loading.gif'
                  , id:'overlight-loading'
                  , style:this.style
                   });
    appendChildNodes(currentDocument().body, knob);
    // can't get control of cursor in iframe area
    // s'ok, FF gives us a wait cursor anyway
    //currentDocument().body.style.cursor = 'wait';
    //$('overlight-iframe').style.cursor = 'wait';
    this.knob = knob;
    this.resize();

  },

  turn_off: function() {
    var knob = $('overlight-loading');
    if (knob) {
      removeElement(knob);
    }
  },

  resize: function() {
    this.reposition();
  },

  reposition: function() {
    if (this.knob) {
      var viewport = getViewportDimensions();

      offset_ = {};
      //offset_.x = document.documentElement.scrollLeft;
      //offset_.y = document.documentElement.scrollTop;

      var pos = {}
      pos.x = /*offset_.x +*/ Math.floor((viewport.w - this.knob.width) / 2);
      pos.y = /*offset_.y +*/ Math.floor((viewport.h - this.knob.height) / 2);
      setElementPosition(this.knob, pos);    }
  }

};
connect(window, 'onresize', Loading, Loading.resize);
connect(window, 'onscroll', Loading, Loading.reposition);





/******************************************************************************\
 States                                                                       */

// Define a State class.
// =====================

function State(name) {
  this.name = name;
};

State.prototype.toString = function() {
  return '<State: ' + this.name + '>';
}

State.prototype.enter = function() {

  // Clear the old state.
  // ====================

  Mask.turn_off();
  Close.turn_off();
  Overlight.destroy();
  states.panes.hide_overlays();
  disconnectAll(currentDocument());


  // Initialize the next state.
  // ==========================

  this.init();


  // Launch an application in the iframe if wanted.
  // ==============================================

  Overlight.create()
  if (this.run) {
    Overlight.show();
    Loading.turn_on();
    Close.turn_on();

    iframeStyle = 'border: none; margin: 0; padding: 0;'
    console.log(this.run);
    iframe = createDOM('iframe', { src:'/foo'//this.run //+ '?' + window.location
                                 , name:'overlight-iframe' // possible security concern?
                                 , id:'overlight-iframe' // possible security concern?
                                 , style:iframeStyle
                                 //, frameReady:0
                                  });
    console.log(iframe.src);
    setElementDimensions(iframe, Overlight.dim);
    appendChildNodes(Overlight.overlight, iframe);

    connect(iframe, 'onload', Loading, Loading.turn_off)
  }

}

State.prototype.init = function() {
  // Override this with state-specific initialization.
}


// Set up specific states.
// =======================

states = {}
states.default_ = null;


// Anonymous
// =========

states.anon = new State('anon');
states.anon.init = function() {

  connect(document, 'onkeypress',
    function(e) {
      var key = e.key();
      if (key.code == 76 || key.code == 12) { // upper-case ell in FF, ? in IE
        if (e.modifier()['ctrl'] || e.modifier()['shift']) {
          e.stop();
          do_login();
        }
      }
    });

}


// iFrame
// ======
// For running another application over top of this page.

states.iframe = new State('iframe');
states.iframe.init = function() {

  connect(document, 'onkeyup',
    function(e) {
      var key = e.key();
      if (key.string == 'KEY_ESCAPE') {
        e.stop();
        connect(document, 'onkeydown',
          function(e) {
            var key = e.key();
            if (key.string == 'KEY_ESCAPE') {
              e.stop();
              states.default_.enter();
            }
          });
      }
    });

  Mask.bgcolor = zetaGreen;
  Mask.opacity = 0.67 // 0.95;
  Mask.turn_on();

}


/* Ready
   =====
   The ready state is the default state for authenticated users. You get a
   "Ready" indicator on the page. Hit <escape> to see panes.

*/

states.ready = new State('ready');
states.ready.sticker = null;
states.ready.init = function() {

  connect(document, 'onkeydown',
    function(e) {
      var key = e.key();
      if (key.string == 'KEY_ESCAPE') {
        e.stop();
        states.panes.enter();
      }

    });

  Ready.turn_on();

}


/* Panes
   =====
   This state shows all the parts of the page that are available for you to
   manage.

*/

states.panes = new State('panes');
states.panes.overlays = new Array(); // an Array of pane overlay HTML objects
states.panes.create = function() {

  // This runs once, on page initialization.
  // =======================================

  var panes = getElementsByTagAndClassName('*', 'overlight-pane');
  for (var i=0, pane; pane=panes[i]; i++) {

    var dim = elementDimensions(pane);
    var pos = elementPosition(pane);
    var overlay = {}


    // The overlay mask is the translucent layer between the link and the page.
    // ========================================================================

    overlay.mask = DIV({'class':'overlight-pane-overlay-mask'});
    overlay.mask.bgcolor = zetaGreen;
    setOpacity(overlay.mask, 0.25);
    setElementDimensions(overlay.mask, dim);
    setElementPosition(overlay.mask, pos);
    hideElement(overlay.mask);

    var dim2 = {}
    dim2.w = (dim.w-8)
    dim2.h = (dim.h-8);
    paddingTop = parseInt(((dim2.h / 2)-60), 10);
    dim3 = {}
    dim3.w = dim2.w;
    dim3.h = dim2.h - paddingTop;


    // The overlay anchor is the link that will open in the iframe.
    // ============================================================

    overlay.a = A({href:getNodeAttribute(pane, 'run')}, i+1);
    overlay.a.style.paddingTop = paddingTop + 'px';
    setElementClass(overlay.a, 'overlight-pane-overlay-text');
    setElementDimensions(overlay.a, dim3);
    setElementPosition(overlay.a, pos);
    hideElement(overlay.a);

    connect(overlay.a, 'onclick',
      function(e) {
        e.stop();
        a = e.src();
        states.iframe.run = a.href;
        console.log(states.iframe.run);
        Overlight.resize();
        states.iframe.enter();
        return false;
      });

    appendChildNodes(currentDocument().body, overlay.a);
    appendChildNodes(currentDocument().body, overlay.mask);

    states.panes.overlays.push(overlay);
  }
}
states.panes.show_overlays = function() {
  for (var i=0, overlay; overlay=states.panes.overlays[i]; i++) {
    showElement(overlay.mask);
    showElement(overlay.a);
  }
}
states.panes.hide_overlays = function() {
  for (var i=0, overlay; overlay=states.panes.overlays[i]; i++) {
    hideElement(overlay.mask);
    hideElement(overlay.a);
  }
}
states.panes.init = function() {

  connect(document, 'onkeyup',
    function(e) {
      var key = e.key();
      if (key.string == 'KEY_ESCAPE') {
        e.stop();
        states.ready.enter();
      }
    });

  Ready.turn_off();
  Mask.bgcolor = zetaGreen;
  Mask.opacity = 0.67;
  Mask.turn_on();
  states.panes.show_overlays();

}


// Login
// =====
// Wrapper for login iframe.

function do_login() {
  states.iframe.run = '/auth/';
  Overlight.dim.w = 640;
  Overlight.dim.h = 480;
  states.iframe.enter();
}




// OnLoad
// ======

connect(window, 'onload',
  function() {
    if (window.self != window.top) { // break out of frames
      window.top.location.replace(window.self.location.href);
    } else { // determine initial state

      // Login
      // =====

      var login = $('overlight-login');
      if (login) {
        var a = A({href:''}, 'Login');
        connect(a, 'onclick',
          function(e) {
            e.stop();
            do_login();
            return false;
          });
        swapDOM(login, a);
        states.default_ = states.anon;
      }


      // Logout
      // ======

      var logout = $('overlight-logout');
      if (logout) {
        var a = A({href:window.location.pathname + '?logout'}, 'Logout');
        swapDOM(logout, a);
        states.panes.create();
        states.default_ = states.ready;
      }
    }

    states.default_.enter();

  });

