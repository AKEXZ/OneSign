package com.onesign.hook.ui;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

/**
 * 模块说明页（可选 UI）。
 */
public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        TextView tv = new TextView(this);
        tv.setText("OneSign Hook 模块已安装\n请在 LSPosed 中勾选并激活本模块，作用域包含：\ncom.ximalaya.ting.android");
        tv.setPadding(48, 48, 48, 48);
        setContentView(tv);
    }
}
