var rancol = function () {
    return function (bg) {
        var hue = Math.floor(Math.random() * 360);
        var hsl = 'hsl('+hue+', 90%, 70%)'; // 100 87.5
        function checkHex(v) {
            return 1 === v.length ? '0'+v : v;
        }
        var data, r, g, b, a,
        cnv = document.createElement('canvas'),
        ctx = cnv.getContext('2d'),
        alpha = /a\(/.test(hsl),
        output = {};
        return cnv.width = cnv.height = 1,
        bg && (ctx.fillStyle = bg, ctx.fillRect(0, 0, 1, 1)),
        ctx.fillStyle = hsl,
        ctx.fillRect(0, 0, 1, 1),
        data = ctx.getImageData(0, 0, 1, 1).data,
        r = data[0],
        g = data[1],
        b = data[2],
        a = (data[3] / 255).toFixed(2),
        output.hex = '#'+checkHex(r.toString(16))+checkHex(g.toString(16))+checkHex(b.toString(16)),
        output.hex;
    };
}();

function colorize(n) {
    var colors = []
    for (var i = 0; i < n; i++ ){
      colors.push(rancol())
    }
    return colors
}