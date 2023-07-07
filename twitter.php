<?php
$PATH = "tweetid.txt";
if($_SERVER['REQUEST_METHOD'] == 'POST'){
    $a = $_POST['tweetid'];
    file_put_contents($PATH, $a, LOCK_EX);
    chmod($PATH, 0644);
    exit;
}
$d = file_get_contents($PATH);
echo '<html><head><title>'.$d.'</title></head><body><a class="twitter-timeline" data-tweet-limit="3" href="https://twitter.com/hoge">Tweets by</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script></body></html>';
