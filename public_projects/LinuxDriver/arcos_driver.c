/*
References

GPIO/Creating/Unloading/reading/Writing/General knowledge: https://youtube.com/playlist?list=PLCGpd0Do5-I3b5TtyqeF1UdyD4C-S-dMa&si=ZiFJXu_m4UhWuRp0
GPIO: https://lwn.net/Articles/532714/
Creating/Unloading: https://www.apriorit.com/dev-blog/195-simple-driver-for-linux-os
Example layout I used as reference: https://olegkutkov.me/2018/03/14/simple-linux-character-device-driver/
Kernel general documentation: https://www.raspberrypi.com/documentation/computers/linux_kernel.html

Auto-updating the display:
    - Looked at this possibility: https://docs.zephyrproject.org/latest/kernel/services/scheduling/index.html
    - Ended up implementing this: https://linuxtv.org/downloads/v4l-dvb-internals/device-drivers/ch01s06.html
*/

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/workqueue.h>

#define BUTTONS 4
#define SEGMENTS 16
#define DEVICE_NAME "arcos_driver"
#define CLASS_NAME "arcos_class"
#define IO_OFFSET 512

static dev_t dev_num;
static struct class *dev_class;
static struct cdev arcos_cdev;

static struct delayed_work button_work;
static unsigned char last_button_state = 0xFF;

static const uint16_t bin_to_seg[16] = { // Exactly 16 bits, lucky me (not using decimal point)
    0b1010011110001001, // 0
    0b0110010000000000,
    0b1011001110010001,
    0b1011011100010001,
    0b0011010000011000,
    0b1001011100011001,
    0b1001011110011001,
    0b1010010000000001,
    0b1011011110011001,
    0b1011010000011001,
    0b1011010010011001,
    0b1011011100100011,
    0b1000001110001001,
    0b1010011100100011,
    0b1001001110011001,
    0b1001000010011001, // F
};

static const int display_gpios[SEGMENTS] = {
    4, 17, 18, 27, 22, 23, 24, 9, 25, 11, 8, 7, 5, 6, 12, 13
};

static const int button_gpios[BUTTONS] = {
    19, 16, 26, 20
};

static void update_display(uint16_t value) {
    for (int i = 0; i < SEGMENTS; i++) {
        int bit = (value >> i) & 1;
        gpio_set_value(display_gpios[i] + IO_OFFSET, bit);
    }
}

static void button_runner(struct work_struct *work) {
    unsigned char state = 0;

    for (int i = 0; i < BUTTONS; i++) {
        if (gpio_get_value(button_gpios[i] + IO_OFFSET))
            state |= (1 << (BUTTONS - 1 - i));
    }

    if (state != last_button_state) {
        update_display(bin_to_seg[state]);
        last_button_state = state;
    }

    schedule_delayed_work(&button_work, msecs_to_jiffies(100));
}

static ssize_t device_read(struct file *file, char __user *buf, size_t len, loff_t *offset) {
    char state[BUTTONS + 1];
    state[BUTTONS] = '\n';

    for (int i = 0; i < BUTTONS; i++) {
        state[i] = gpio_get_value(button_gpios[i] + IO_OFFSET) ? '1' : '0';
    }

    return copy_to_user(buf, state, BUTTONS + 1) ? -EFAULT : BUTTONS + 1;
}

static ssize_t device_write(struct file *file, const char __user *buf, size_t len, loff_t *offset) {
    char kbuf[5] = {0};
    unsigned char index = 0;

    if (len < 4 || copy_from_user(kbuf, buf, 4))
        return -EINVAL;

    for (int i = 0; i < 4; i++) { // very nice
        if (kbuf[i] == '1') index |= (1 << (3 - i)); // shift left 1 by 3-i
        else if (kbuf[i] != '0') return -EINVAL;
    }

    update_display(bin_to_seg[index]);
    return len;
}

static struct file_operations fops = { // must be after device_read and write
    .owner = THIS_MODULE,
    .read = device_read,
    .write = device_write,
};

static int init_gpios(void) {
    for (int i = 0; i < BUTTONS; i++) {
        int gpio = button_gpios[i] + IO_OFFSET;
        gpio_request(gpio, "arcos_button");
        gpio_direction_input(gpio);
    }
    for (int i = 0; i < SEGMENTS; i++) {
        int gpio = display_gpios[i] + IO_OFFSET;
        gpio_request(gpio, "arcos_display");
        gpio_direction_output(gpio, 0);
    }
    return 0;
}

static void free_gpios(void) {
    for (int i = 0; i < SEGMENTS; i++)
        gpio_free(display_gpios[i] + IO_OFFSET);
    for (int i = 0; i < BUTTONS; i++)
        gpio_free(button_gpios[i] + IO_OFFSET);
}

static int __init arcos_init(void) {
    if (alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME) < 0) // Can't allocate the device for some reason
        return -1;

    // i found you could check for errors everywhere here but tutorials and examples skip them
    // and this is the only thing my raspberry runs so it never errors anyway
    dev_class = class_create(CLASS_NAME);
    device_create(dev_class, NULL, dev_num, NULL, DEVICE_NAME);

    cdev_init(&arcos_cdev, &fops);
    cdev_add(&arcos_cdev, dev_num, 1);

    init_gpios();

    INIT_DELAYED_WORK(&button_work, button_runner);
    schedule_delayed_work(&button_work, msecs_to_jiffies(100)); // a jiffy represents a tick of the system timer interrupt

    printk(KERN_INFO "Arcos driver loaded\n");
    return 0;
}

static void __exit arcos_exit(void) {
    cancel_delayed_work_sync(&button_work);
    free_gpios();
    cdev_del(&arcos_cdev);
    device_destroy(dev_class, dev_num);
    class_destroy(dev_class);
    unregister_chrdev_region(dev_num, 1);
    printk(KERN_INFO "Arcos driver unloaded\n");
}

module_init(arcos_init);
module_exit(arcos_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Ivan Arcos");
MODULE_DESCRIPTION("Auto-updating 16-segment display from 4 DIP switch");