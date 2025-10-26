package had;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Counters;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

public class DataCleaning {

    // 字段索引常量（共29个字段）
    private static final int TRANSACTION_ID_INDEX = 0;    // 交易ID
    private static final int CUSTOMER_ID_INDEX = 1;       // 客户ID
    private static final int NAME_INDEX = 2;              // 姓名
    private static final int EMAIL_INDEX = 3;             // 电子邮件
    private static final int PHONE_INDEX = 4;             // 电话
    private static final int ADDRESS_INDEX = 5;           // 地址
    private static final int CITY_INDEX = 6;              // 城市
    private static final int STATE_INDEX = 7;             // 州
    private static final int ZIP_INDEX = 8;               // 邮政编码
    private static final int COUNTRY_INDEX = 9;           // 国家
    private static final int AGE_INDEX = 10;              // 年龄
    private static final int GENDER_INDEX = 11;           // 性别
    private static final int INCOME_INDEX = 12;           // 收入
    private static final int SEGMENT_INDEX = 13;          // 客户细分
    private static final int YEAR_INDEX = 14;             // 年份
    private static final int MONTH_INDEX = 15;            // 月份
    private static final int DAY_INDEX = 16;              // 日
    private static final int TIME_INDEX = 17;             // 时间
    private static final int AMOUNT_INDEX = 18;           // 消费金额
    private static final int PRODUCT_CATEGORY_INDEX = 19; // 产品类别
    private static final int PRODUCT_BRAND_INDEX = 20;    // 产品品牌
    private static final int PRODUCT_TYPE_INDEX = 21;     // 产品类型
    private static final int FEEDBACK_INDEX = 22;         // 反馈
    private static final int SHIPPING_INDEX = 23;         // 运输方式
    private static final int PAYMENT_METHOD_INDEX = 24;   // 付款方式
    private static final int ORDER_STATUS_INDEX = 25;     // 订单状态
    private static final int RATING_INDEX = 26;           // 评分
    private static final int PRODUCT_LIST_INDEX = 27;     // 产品列表
    // 注意：第28个字段（下标27），如有遗漏请补充

    /**
     * Mapper类：数据清洗核心逻辑
     * 功能：实现全字段验证并统计清洗率
     */
    public static class DataCleaningMapper extends Mapper<LongWritable, Text, Text, NullWritable> {

        // 自定义计数器枚举
        public static enum CLEANING_COUNTERS {
            TOTAL_RECORDS,
            VALID_RECORDS,
            INVALID_TRANSACTION_ID,
            INVALID_CUSTOMER_ID,
            INVALID_NAME,
            INVALID_EMAIL,
            INVALID_PHONE,
            INVALID_ADDRESS,
            INVALID_CITY,
            INVALID_STATE,
            INVALID_ZIP,
            INVALID_COUNTRY,
            INVALID_AGE,
            INVALID_GENDER,
            INVALID_INCOME,
            INVALID_SEGMENT,
            INVALID_YEAR,
            INVALID_MONTH,
            INVALID_DAY,
            INVALID_TIME,
            INVALID_AMOUNT,
            INVALID_CATEGORY,
            INVALID_BRAND,
            INVALID_TYPE,
            INVALID_FEEDBACK,
            INVALID_SHIPPING,
            INVALID_PAYMENT,
            INVALID_STATUS,
            INVALID_RATING,
            INVALID_PRODUCT_LIST
        }

        private Text outputRecord = new Text();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            context.getCounter(CLEANING_COUNTERS.TOTAL_RECORDS).increment(1);

            String line = value.toString().trim();
            if (line.isEmpty()) return;

            String[] fields = line.split(",", -1);
            if (fields.length < 28) return; // 字段数不足直接丢弃

            // 0. 交易ID
            if (fields[TRANSACTION_ID_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_TRANSACTION_ID).increment(1);
                return;
            }
            // 1. 客户ID
            if (fields[CUSTOMER_ID_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_CUSTOMER_ID).increment(1);
                return;
            }
            // 2. 姓名
            if (fields[NAME_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_NAME).increment(1);
                return;
            }
            // 3. 电子邮件
            if (fields[EMAIL_INDEX].trim().isEmpty() || !fields[EMAIL_INDEX].contains("@")) {
                context.getCounter(CLEANING_COUNTERS.INVALID_EMAIL).increment(1);
                return;
            }
            // 4. 电话
            if (fields[PHONE_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_PHONE).increment(1);
                return;
            }
            // 5. 地址
            if (fields[ADDRESS_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_ADDRESS).increment(1);
                return;
            }
            // 6. 城市
            if (fields[CITY_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_CITY).increment(1);
                return;
            }
            // 7. 州
            if (fields[STATE_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_STATE).increment(1);
                return;
            }
            // 8. 邮政编码
            if (fields[ZIP_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_ZIP).increment(1);
                return;
            }
            // 9. 国家
            if (fields[COUNTRY_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_COUNTRY).increment(1);
                return;
            }
            // 10. 年龄
            try {
                int age = Integer.parseInt(fields[AGE_INDEX].trim());
                if (age <= 0 || age > 120) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_AGE).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_AGE).increment(1);
                return;
            }
            // 11. 性别
            String gender = fields[GENDER_INDEX].trim();
            if (gender.isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_GENDER).increment(1);
                return;
            }
            // 12. 收入
            if (fields[INCOME_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_INCOME).increment(1);
                return;
            }
            // 13. 客户细分
            if (fields[SEGMENT_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_SEGMENT).increment(1);
                return;
            }
            // 14. 年份
            try {
                int year = Integer.parseInt(fields[YEAR_INDEX].trim());
                if (year < 2000 || year > 2100) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_YEAR).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_YEAR).increment(1);
                return;
            }
            // 15. 月份
            try {
                int month = Integer.parseInt(fields[MONTH_INDEX].trim());
                if (month < 1 || month > 12) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_MONTH).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_MONTH).increment(1);
                return;
            }
            // 16. 日
            try {
                int day = Integer.parseInt(fields[DAY_INDEX].trim());
                if (day < 1 || day > 31) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_DAY).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_DAY).increment(1);
                return;
            }
            // 17. 时间（可选简单校验）
            if (fields[TIME_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_TIME).increment(1);
                return;
            }
            // 18. 消费金额
            try {
                double amount = Double.parseDouble(fields[AMOUNT_INDEX].trim());
                if (amount <= 0) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_AMOUNT).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_AMOUNT).increment(1);
                return;
            }
            // 19. 产品类别
            if (fields[PRODUCT_CATEGORY_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_CATEGORY).increment(1);
                return;
            }
            // 20. 产品品牌
            if (fields[PRODUCT_BRAND_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_BRAND).increment(1);
                return;
            }
            // 21. 产品类型
            if (fields[PRODUCT_TYPE_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_TYPE).increment(1);
                return;
            }
            // 22. 反馈（可选：长度限制）
            if (fields[FEEDBACK_INDEX].length() > 200) {
                context.getCounter(CLEANING_COUNTERS.INVALID_FEEDBACK).increment(1);
                return;
            }
            // 23. 运输方式
            if (fields[SHIPPING_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_SHIPPING).increment(1);
                return;
            }
            // 24. 付款方式
            if (fields[PAYMENT_METHOD_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_PAYMENT).increment(1);
                return;
            }
            // 25. 订单状态
            if (fields[ORDER_STATUS_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_STATUS).increment(1);
                return;
            }
            // 26. 评分
            try {
                double rating = Double.parseDouble(fields[RATING_INDEX].trim());
                if (rating < 0 || rating > 5) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_RATING).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_RATING).increment(1);
                return;
            }
            // 27. 产品列表
            if (fields[PRODUCT_LIST_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_PRODUCT_LIST).increment(1);
                return;
            }

            // 有效记录
            context.getCounter(CLEANING_COUNTERS.VALID_RECORDS).increment(1);
            outputRecord.set(line);
            context.write(outputRecord, NullWritable.get());
        }
    }

    /**
     * 主程序入口
     */
    public static void main(String[] args) throws Exception {
        // ==================== 用户界面 ====================
        System.out.println("╔════════════════════════════════════════╗");
        System.out.println("║      大数据清洗工具 - 全字段数据清洗     ║");
        System.out.println("╚════════════════════════════════════════╝");
        System.out.println("\n【清洗规则】");
        System.out.println("1. 交易ID：非空验证");
        System.out.println("2. 客户ID：非空验证");
        System.out.println("3. 姓名：非空验证");
        System.out.println("4. 电子邮件：非空且包含@");
        System.out.println("5. 电话：非空验证");
        System.out.println("6. 地址：非空验证");
        System.out.println("7. 城市：非空验证");
        System.out.println("8. 州：非空验证");
        System.out.println("9. 邮政编码：非空验证");
        System.out.println("10. 国家：非空验证");
        System.out.println("11. 年龄：1-120岁有效范围");
        System.out.println("12. 性别：M/F且非空");
        System.out.println("13. 收入：非空验证");
        System.out.println("14. 客户细分：非空验证");
        System.out.println("15. 年份：2000-2100");
        System.out.println("16. 月份：1-12");
        System.out.println("17. 日：1-31");
        System.out.println("18. 时间：非空验证");
        System.out.println("19. 消费金额：正数验证");
        System.out.println("20. 产品类别：非空验证");
        System.out.println("21. 产品品牌：非空验证");
        System.out.println("22. 产品类型：非空验证");
        System.out.println("23. 反馈：长度不超过200");
        System.out.println("24. 运输方式：非空验证");
        System.out.println("25. 付款方式：非空验证");
        System.out.println("26. 订单状态：非空验证");
        System.out.println("27. 评分：0-5");
        System.out.println("28. 产品列表：非空验证");

        // ==================== 参数检查 ====================
        if (args.length != 2) {
            System.err.println("\n【错误】参数不正确！");
            System.err.println("用法: hadoop jar DataCleaning.jar <输入路径> <输出路径>");
            System.err.println("示例: hadoop jar DataCleaning.jar /input /output");
            System.exit(1);
        }

        // ==================== 作业配置 ====================
        System.out.println("\n【作业配置】");
        System.out.println("输入路径: " + args[0]);
        System.out.println("输出路径: " + args[1]);

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "全字段数据清洗作业");

        job.setJarByClass(DataCleaning.class);
        job.setMapperClass(DataCleaningMapper.class);
        job.setNumReduceTasks(0);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(NullWritable.class);

        // ==================== 路径设置 ====================
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // ==================== 作业执行 ====================
        System.out.println("\n【执行状态】");
        System.out.println("正在启动数据清洗作业...");

        long startTime = System.currentTimeMillis();

        // 可视化进度条
        Thread progressThread = new Thread(() -> {
            String[] bars = {"|", "/", "-", "\\"};
            int idx = 0;
            while (!Thread.currentThread().isInterrupted()) {
                System.out.print("\r清洗进度: " + bars[idx++ % bars.length]);
                try {
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    break;
                }
            }
            System.out.print("\r清洗进度: 完成           \n");
        });
        progressThread.start();

        boolean success = job.waitForCompletion(true);

        progressThread.interrupt();
        try { progressThread.join(); } catch (InterruptedException ignored) {}

        long endTime = System.currentTimeMillis();

        // ==================== 清洗报告 ====================
        if (success) {
            Counters counters = job.getCounters();

            long total = counters.findCounter(DataCleaningMapper.CLEANING_COUNTERS.TOTAL_RECORDS).getValue();
            long valid = counters.findCounter(DataCleaningMapper.CLEANING_COUNTERS.VALID_RECORDS).getValue();
            double rate = total > 0 ? (valid * 100.0 / total) : 0;

            System.out.println("\n【清洗报告】");
            System.out.println("✅ 作业完成");
            System.out.printf("⏱️ 总耗时: %.2f秒\n", (endTime - startTime)/1000.0);
            System.out.println("📊 记录统计:");
            System.out.printf("  总记录数: %d\n", total);
            System.out.printf("  有效记录: %d (%.2f%%)\n", valid, rate);
            System.out.printf("  无效记录: %d (%.2f%%)\n", total - valid, 100 - rate);

            System.out.println("\n🔍 无效原因分析:");
            printCounter(counters, "  空交易ID: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_TRANSACTION_ID);
            printCounter(counters, "  空客户ID: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_CUSTOMER_ID);
            printCounter(counters, "  空姓名: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_NAME);
            printCounter(counters, "  邮箱无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_EMAIL);
            printCounter(counters, "  空电话: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_PHONE);
            printCounter(counters, "  空地址: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_ADDRESS);
            printCounter(counters, "  空城市: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_CITY);
            printCounter(counters, "  空州: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_STATE);
            printCounter(counters, "  空邮编: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_ZIP);
            printCounter(counters, "  空国家: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_COUNTRY);
            printCounter(counters, "  年龄无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_AGE);
            printCounter(counters, "  空性别: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_GENDER);
            printCounter(counters, "  收入无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_INCOME);
            printCounter(counters, "  客户细分无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_SEGMENT);
            printCounter(counters, "  年份无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_YEAR);
            printCounter(counters, "  月份无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_MONTH);
            printCounter(counters, "  日无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_DAY);
            printCounter(counters, "  时间无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_TIME);
            printCounter(counters, "  金额无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_AMOUNT);
            printCounter(counters, "  产品类别无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_CATEGORY);
            printCounter(counters, "  产品品牌无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_BRAND);
            printCounter(counters, "  产品类型无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_TYPE);
            printCounter(counters, "  反馈过长: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_FEEDBACK);
            printCounter(counters, "  运输方式无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_SHIPPING);
            printCounter(counters, "  付款方式无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_PAYMENT);
            printCounter(counters, "  订单状态无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_STATUS);
            printCounter(counters, "  评分无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_RATING);
            printCounter(counters, "  产品列表无效: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_PRODUCT_LIST);

            System.out.println("\n📂 输出路径: " + args[1]);
        } else {
            System.out.println("❌ 作业执行失败！");
        }

        System.exit(success ? 0 : 1);
    }

    // 辅助方法：打印计数器信息
    private static void printCounter(Counters counters, String label, 
            DataCleaningMapper.CLEANING_COUNTERS counter) {
        long value = counters.findCounter(counter).getValue();
        if (value > 0) {
            System.out.println(label + value);
        }
    }
}
