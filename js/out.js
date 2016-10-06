var tests = [
[4, (function () {
    function add (x, y) {
        return (x + y);
    }
    return add(2, 2);
})],
[4, (function () {
    var add2 = add;
    function add (x, y) {
        return (x + y);
    }
    return add2(2, 2);
})],
[4, (function () {
    return (2 + 2);
})],
["Hello world!", (function () {
    function add (x, y) {
        return (x + y);
    }
    return add("Hello ", "world!");
})],
["Hello world!", (function () {
    function add (x, y) {
        return (x + y);
    }
    return add('Hello ', 'world!');
})],
[5, (function () {
    var len = _.size;
    return len("hello");
})],
[2, (function () {
    var len = _.size;
    return len(["hello ", "world!"]);
})],
[2, (function () {
    var len = _.size;
    return len(["hello ", "world!"]);
})],
[0, (function () {
    var len = _.size;
    return len([]);
})],
[0, (function () {
    var len = _.size;
    return len([]);
})],
[2, (function () {
    var len = _.size;
    return len({"foo": 42, "bar": 23});
})],
[1, (function () {
    var len = _.size;
    return len({"foo": 42});
})],
[3, (function () {
    function add (x, y) {
        return (x + y);
    }
    return (function(x,y){return add(x, y);})(1, 2);
})],
[3, (function () {
    function add (x, y) {
        return (x + y);
    }
    return (function(x, y){return add(x, y);})(1, 2);
})],
[65, (function () {
    function add (x, y) {
        return (x + y);
    }
    return (function(x,y){return add(x, y);})(23, 42);
})],
[4, (function () {
    function add (x, y) {
        return (x + y);
    }
    return (function(x){return add(x, x);})(2);
})],
[4, (function () {
    function add (x, y) {
        return (x + y);
    }
    return (function(x){return add(x, x);})(add(1, 1));
})],
[2, (function () {
    function inc (x) {
        return add(x, 1);
    }
    function add (x, y) {
        return (x + y);
    }
    return inc(1);
})],
[42, (function () {
    return (true ? 42 : 23);
})],
[23, (function () {
    return (false ? 42 : 23);
})],
[23, (function () {
    function eq (a, b) {
        return (a == b);
    }
    return (eq(42, 23) ? 42 : 23);
})],
[true, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return even(0);
})],
[false, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return odd(0);
})],
[false, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return even(1);
})],
[true, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return odd(1);
})],
[true, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return even(42);
})],
[false, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return odd(42);
})],
[false, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return even(23);
})],
[true, (function () {
    function even (n) {
        return (eq(n, 0) ? true : odd(sub(n, 1)));
    }
    function sub (a, b) {
        return (a - b);
    }
    function odd (n) {
        return (eq(n, 0) ? false : even(sub(n, 1)));
    }
    function eq (a, b) {
        return (a == b);
    }
    return odd(23);
})],
[42, (function () {
    var answer = 42;
    return answer;
})],
["bar", (function () {
    var foo = "bar";
    return foo;
})],
[23, (function () {
    function sub (a, b) {
        return (a - b);
    }
    var answer = 42;
    return sub(answer, 19);
})],
[120, (function () {
    function factorial (n) {
        return ((n == 0) ? 1 : (n * factorial((n - 1))));
    }
    return factorial(5);
})],
[42, (function () {
    function ans () {
        return 42;
    }
    return ans();
})],
[6, (function () {
    return (function(x, y){return (x + y);})(...([4, 2]));
})],
[[1, 2, 3], (function () {
    var mkl = (function(...xs){return xs;});
    return mkl(1, (1 + 1), 3);
})],
[{"foo": 42, "bar": 23}, (function () {
    var add_dict = (function(a,b){return _.defaults(b,a);});
    return add_dict({"foo": 42}, {"bar": 23});
})],
[{"foo": 42, "bar": 23, "_": 1}, (function () {
    var add_dict = (function(a,b){return _.defaults(b,a);});
    return add_dict({"foo": 42, "_": 1}, {"bar": 23, "_": 1});
})],
];