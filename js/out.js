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
];