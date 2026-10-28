<?php
/**
 * Обработчик заявок с сайта → Telegram + e-mail.
 * Работает на любом PHP-хостинге (Beget, Timeweb, REG.RU и т.п.), PHP 7.4+.
 *
 * Настройка: скопируйте config.example.php в config.php и заполните.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

$cfgFile = __DIR__ . '/config.php';
$cfg = file_exists($cfgFile) ? require $cfgFile : [];
$cfg += [
    'telegram_token' => getenv('TG_TOKEN') ?: '',
    'telegram_chat'  => getenv('TG_CHAT') ?: '',
    'email_to'       => getenv('LEAD_EMAIL') ?: '',
    'email_from'     => 'noreply@' . ($_SERVER['HTTP_HOST'] ?? 'localhost'),
    'allowed_origin' => '',
];

function out(int $code, array $data): void { http_response_code($code); echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['ok' => false, 'error' => 'method']);

// Защита от отправки с чужих сайтов
if ($cfg['allowed_origin'] && isset($_SERVER['HTTP_ORIGIN']) && $_SERVER['HTTP_ORIGIN'] !== $cfg['allowed_origin']) out(403, ['ok' => false]);

$raw = file_get_contents('php://input') ?: '';
$in = json_decode($raw, true);
if (!is_array($in)) $in = $_POST;

// Honeypot: боты заполняют скрытое поле
if (!empty($in['website'])) out(200, ['ok' => true]);

$clean = static fn($v, int $max = 300): string => mb_substr(trim(strip_tags((string)($v ?? ''))), 0, $max);
$name    = $clean($in['name'] ?? '', 80);
$phone   = preg_replace('/[^\d+]/', '', (string)($in['phone'] ?? ''));
$message = $clean($in['message'] ?? '', 2000);
$source  = $clean($in['source'] ?? '', 120);
$extra   = $clean($in['extra'] ?? '', 500);
$page    = $clean($in['page'] ?? '', 300);
$day     = $clean($in['day'] ?? '', 60);
$time    = $clean($in['time'] ?? '', 10);

if ($name === '' || strlen(preg_replace('/\D/', '', $phone)) < 11) out(422, ['ok' => false, 'error' => 'validation']);
if (empty($in['consent'])) out(422, ['ok' => false, 'error' => 'consent']);

// Простой rate-limit: не чаще 1 заявки в 20 секунд с одного IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$lock = sys_get_temp_dir() . '/lead_' . md5($ip);
if (file_exists($lock) && time() - filemtime($lock) < 20) out(429, ['ok' => false, 'error' => 'rate']);
@touch($lock);

$lines = [
    '🏠 Новая заявка с сайта',
    "Имя: $name",
    "Телефон: $phone",
    $message ? "Задача: $message" : null,
    $extra ? "Расчёт: $extra" : null,
    ($day || $time) ? 'Замер: ' . trim("$day $time") : null,
    $source ? "Источник: $source" : null,
    $page ? "Страница: $page" : null,
    'Время: ' . date('d.m.Y H:i'),
];
$text = implode("\n", array_filter($lines));
$sent = false;

if ($cfg['telegram_token'] && $cfg['telegram_chat']) {
    $ctx = stream_context_create(['http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/json\r\n",
        'content' => json_encode(['chat_id' => $cfg['telegram_chat'], 'text' => $text, 'disable_web_page_preview' => true]),
        'timeout' => 8,
    ]]);
    $res = @file_get_contents("https://api.telegram.org/bot{$cfg['telegram_token']}/sendMessage", false, $ctx);
    $sent = $res !== false || $sent;
}

if ($cfg['email_to']) {
    $headers = "From: {$cfg['email_from']}\r\nContent-Type: text/plain; charset=utf-8\r\n";
    $sent = @mail($cfg['email_to'], '=?UTF-8?B?' . base64_encode('Заявка с сайта: ' . $name) . '?=', $text, $headers) || $sent;
}

// Резервная копия всех заявок (папка закрыта от веба через .htaccess)
$dir = __DIR__ . '/leads';
if (!is_dir($dir)) @mkdir($dir, 0750, true);
@file_put_contents($dir . '/' . date('Y-m') . '.log', $text . "\n---\n", FILE_APPEND | LOCK_EX);

out($sent ? 200 : 500, ['ok' => $sent]);
