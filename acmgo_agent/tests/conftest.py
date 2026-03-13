"""pytest fixtures。"""
import os
import shutil
import tempfile
import sys
from pathlib import Path

import pytest


# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def tmp_work_dir():
    """创建临时工作目录。"""
    temp_dir = tempfile.mkdtemp(prefix="acmgo_test_")
    yield temp_dir
    # 清理
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_cpp_files(tmp_work_dir):
    """在工作目录中创建简单的 C++ 示例文件。"""
    # Simplified testlib.h for testing purposes
    testlib_h = """\
#pragma once
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <cstdlib>
#include <algorithm>

using namespace std;

// Simplified testlib for testing
mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
mt19937 rnd = rng;

inline int opt(int) { return 0; }

// Stub functions for validator/generator
void registerGen(int, char*[], int) {}
void registerValidation() {}

class InStream {
    istringstream ss;
public:
    InStream() {}
    InStream(const string& s) : ss(s) {}
    int readInt(int minv, int maxv) {
        int x; ss >> x; return x;
    }
    void readEoln() { ss.ignore(); }
    void readSpace() {}
    void readEof() {}
} inf;
"""

    # Simple solution - A + B problem
    simple_sol_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
    }
    return 0;
}
"""

    simple_brute_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
    }
    return 0;
}
"""

    # Generator that creates test data
    simple_gen_cpp = """\
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    int seed = (argc > 1) ? atoi(argv[1]) : 1;
    int type = (argc > 2) ? atoi(argv[2]) : 1;
    int n_min = (argc > 3) ? atoi(argv[3]) : 1;
    int n_max = (argc > 4) ? atoi(argv[4]) : 10;
    int t_min = (argc > 5) ? atoi(argv[5]) : 1;
    int t_max = (argc > 6) ? atoi(argv[6]) : 3;

    rng.seed(seed);

    int t = t_min + (rng() % (t_max - t_min + 1));
    cout << t << endl;
    for (int i = 0; i < t; i++) {
        int a = rng() % 1000;
        int b = rng() % 1000;
        cout << a << " " << b << endl;
    }
    return 0;
}
"""

    # Validator stub
    simple_val_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    int t = inf.readInt(1, 10);
    inf.readEoln();
    for (int i = 0; i < t; i++) {
        inf.readInt(0, 1000);
        inf.readSpace();
        inf.readInt(0, 1000);
        inf.readEoln();
    }
    inf.readEof();
    return 0;
}
"""

    # Write files
    with open(os.path.join(tmp_work_dir, "testlib.h"), "w", encoding="utf-8") as f:
        f.write(testlib_h)
    with open(os.path.join(tmp_work_dir, "sol.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_sol_cpp)
    with open(os.path.join(tmp_work_dir, "brute.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_brute_cpp)
    with open(os.path.join(tmp_work_dir, "gen.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_gen_cpp)
    with open(os.path.join(tmp_work_dir, "val.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_val_cpp)

    return tmp_work_dir


@pytest.fixture
def valid_problem_dir(tmp_work_dir):
    """创建一个完整的示例题目目录结构。"""
    # Simplified testlib.h for testing purposes
    testlib_h = """\
#pragma once
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <cstdlib>
#include <algorithm>

using namespace std;

// Simplified testlib for testing
mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
mt19937 rnd = rng;

inline int opt(int) { return 0; }

// Stub functions for validator/generator
void registerGen(int, char*[], int) {}
void registerValidation() {}

class InStream {
    istringstream ss;
public:
    InStream() {}
    InStream(const string& s) : ss(s) {}
    int readInt(int minv, int maxv) {
        int x; ss >> x; return x;
    }
    void readEoln() { ss.ignore(); }
    void readSpace() {}
    void readEof() {}
} inf;
"""

    # Simple solution - A + B problem
    simple_sol_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
    }
    return 0;
}
"""

    simple_brute_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
    }
    return 0;
}
"""

    # Generator that creates test data
    simple_gen_cpp = """\
#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    int seed = (argc > 1) ? atoi(argv[1]) : 1;
    int type = (argc > 2) ? atoi(argv[2]) : 1;
    int n_min = (argc > 3) ? atoi(argv[3]) : 1;
    int n_max = (argc > 4) ? atoi(argv[4]) : 10;
    int t_min = (argc > 5) ? atoi(argv[5]) : 1;
    int t_max = (argc > 6) ? atoi(argv[6]) : 3;

    rng.seed(seed);

    int t = t_min + (rng() % (t_max - t_min + 1));
    cout << t << endl;
    for (int i = 0; i < t; i++) {
        int a = rng() % 1000;
        int b = rng() % 1000;
        cout << a << " " << b << endl;
    }
    return 0;
}
"""

    # Validator stub
    simple_val_cpp = """\
#include "testlib.h"
using namespace std;

int main() {
    int t = inf.readInt(1, 10);
    inf.readEoln();
    for (int i = 0; i < t; i++) {
        inf.readInt(0, 1000);
        inf.readSpace();
        inf.readInt(0, 1000);
        inf.readEoln();
    }
    inf.readEof();
    return 0;
}
"""

    # Write source files
    with open(os.path.join(tmp_work_dir, "testlib.h"), "w", encoding="utf-8") as f:
        f.write(testlib_h)
    with open(os.path.join(tmp_work_dir, "sol.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_sol_cpp)
    with open(os.path.join(tmp_work_dir, "brute.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_brute_cpp)
    with open(os.path.join(tmp_work_dir, "gen.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_gen_cpp)
    with open(os.path.join(tmp_work_dir, "val.cpp"), "w", encoding="utf-8") as f:
        f.write(simple_val_cpp)

    # Create README
    readme = """# A + B Problem

给定两个整数 A 和 B，输出它们的和。

## Input
第一行包含一个整数 T，表示测试用例的数量。
接下来 T 行，每行包含两个整数 A 和 B。

## Output
对于每个测试用例，输出 A + B。
"""
    with open(os.path.join(tmp_work_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    return tmp_work_dir
