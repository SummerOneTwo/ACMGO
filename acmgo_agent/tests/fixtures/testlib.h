#include <bits/stdc++.h>
using namespace std;

#define forn(i, n) for(int i = 0; i < (n); ++i)
#define forr(i, l, r) for(int i = (l); i <= (r); ++i)
#define forrev(i, n) for(int i = (n) - 1; i >= 0; --i)
#define forn64(i, n) for(ll i = 0; i < (n); ++i)
#define forr64(i, l, r) for(ll i = (l); i <= (r); ++i)

#define all(x) x.begin(), x.end()
#define rall(x) x.rbegin(), x.rend()
#define pb push_back
#define fi first
#define se second
#define mp make_pair

typedef long long ll;
typedef long double ld;
typedef pair<int, int> pii;
typedef pair<ll, ll> pll;

mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

int rnd(int l, int r) { return uniform_int_distribution<int>(l, r)(rng); }
ll rnd64(ll l, ll r) { return uniform_int_distribution<ll>(l, r)(rng); }

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    return 0;
}
