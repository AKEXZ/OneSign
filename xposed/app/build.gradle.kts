plugins {
    id("com.android.application")
}

android {
    namespace = "com.onesign.hook"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.onesign.hook"
        minSdk = 21
        targetSdk = 34
        versionCode = 12
        versionName = "2.2.0"
    }

    signingConfigs {
        create("release") {
            storeFile = file("../signing/onesign.jks")
            storePassword = "onesign2026"
            keyAlias = "onesign"
            keyPassword = "onesign2026"
            enableV1Signing = true
            enableV2Signing = true
            enableV3Signing = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName("release")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    // Xposed API：仅编译期依赖，不打包进 APK（由框架运行时提供）
    compileOnly("de.robv.android.xposed:api:82")
    compileOnly("de.robv.android.xposed:api:82:sources")
}
