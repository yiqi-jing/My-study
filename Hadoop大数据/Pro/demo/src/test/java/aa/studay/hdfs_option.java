package aa.studay;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.junit.Before;
import org.junit.Test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class hdfs_option {
    FileSystem fs=null;

    @Before
    public void init() throws IOException {
        //构建配置参数对象：Configuration
        Configuration conf = new Configuration();
        //设置参数，指定要访问的文件系统的类型：HDFS文件系统
        conf.set("fs.defaultFS","hdfs://node1:9000");
        //设置客户端的访问身份，以root身份访问HDFS
        System.setProperty("HADOOP_USER_NAME","root");
        //通过FileSystem类静态方法，获取客户端访问对象
        fs = FileSystem.get(conf);
    }
    /* 
     * 实验任务1：HDFS Shell操作
    （1）创建一个新目录 /user/experiment。
    （2）上传一个本地文件到 HDFS 的 /user/experiment 目录。
    （3）查看 HDFS 中 /user/experiment 目录的内容。
    （4）下载 HDFS 中的 /user/experiment/目录到本地 /tmp 目录。
    （5）删除 HDFS 中的 /user/experiment 目录及其内容。
    上述分开测试
     */
    @Test
    public void testHDFSShell() throws IOException {
        // 创建目录
        Path dirPath = new Path("/user/experiment");
        if (!fs.exists(dirPath)) {
            fs.mkdirs(dirPath);
            System.out.println("目录创建成功: " + dirPath);
        } else {
            System.out.println("目录已存在: " + dirPath);
        }
    }
    //上传文件（简单上传）
    @Test
     public void upload() throws IOException {
        // 创建本地路径的Path对象
        Path src = new Path("F:/Hadoop上传文件/word.txt");
        // 创建HDFS路径的Path对象
        Path dst = new Path("/user/experiment/word.txt");
        // 上传文件
        fs.copyFromLocalFile(src,dst);
        // 关闭资源
        fs.close();
    }
    // 查看目录内容
    @Test
    public void testListDirectory() throws IOException {
        Path dirPath = new Path("/user/experiment");
        if (fs.exists(dirPath)) {
            FileStatus[] fileStatuses = fs.listStatus(dirPath);
            System.out.println("目录内容:");
            for (FileStatus fileStatus : fileStatuses) {
                System.out.println("文件名: " + fileStatus.getPath().getName());
                System.out.println("文件大小: " + fileStatus.getLen());
                System.out.println("-----------------------------");
            }
        } else {
            System.out.println("目录不存在: " + dirPath);
        }
    }
    // 下载文件
    @Test
    public void testDownloadFile() throws IOException {
        Path hdfsFilePath = new Path("/user/experiment/word.txt");
        Path localDownloadPath = new Path("F:\\Hadoop下载文件\\word.txt");
        if (fs.exists(hdfsFilePath)) {
            fs.copyToLocalFile(hdfsFilePath, localDownloadPath);
            System.out.println("文件下载成功: " + localDownloadPath);
        } else {
            System.out.println("文件不存在: " + hdfsFilePath);
        }
    }
    // 删除目录及其内容
    @Test
    public void testDeleteDirectory() throws IOException {
        Path dirPath = new Path("/user/experiment");
        if (fs.exists(dirPath)) {
            fs.delete(dirPath, true);
            System.out.println("目录及其内容删除成功: " + dirPath);
        } else {
            System.out.println("目录不存在: " + dirPath);
        }
    }
    /* 
     * 实验任务2：HDFS Java API操作
    编写Java程序实现以下功能：
    （1）在HDFS根目录下创建目录Java
    （2）将本地test.txt上传到HDFS的Java目录下。
    （3）将test.txt下载到本地("F:\Hadoop下载文件")，同时将文件重命名为download。
    （4）查看HDFS根目录下所有文件的元数据信息（包括文件属性信息、数据块信息）。
    （5）读取HDFS里test.txt文件中内容并打印到控制台。
    （6）向HDFS里的test.txt文件追加内容“你好，Hadoop！”。
     */
    // 创建目录
    @Test
    public void testCreateDirectory() throws IOException {
        Path dirPath = new Path("/Java");
        if (!fs.exists(dirPath)) {
            fs.mkdirs(dirPath);
            System.out.println("目录创建成功: " + dirPath);
        } else {
            System.out.println("目录已存在: " + dirPath);
        }
    }
    // 上传文件
    @Test
    public void testUploadFileToJava() throws IOException {
        Path localFilePath = new Path("F:\\Hadoop上传文件\\word.txt");
        Path hdfsFilePath = new Path("/Java/word.txt");
        if (fs.exists(hdfsFilePath)) {
            System.out.println("文件已存在: " + hdfsFilePath);
        } else {
            fs.copyFromLocalFile(localFilePath, hdfsFilePath);
            System.out.println("文件上传成功: " + hdfsFilePath);
        }
    }
    // 下载文件
    @Test
    public void testDownloadFileToLocal() throws IOException {
        Path hdfsFilePath = new Path("/Java/word.txt");
        Path localDownloadPath = new Path("F:\\Hadoop下载文件\\download.txt");
        if (fs.exists(hdfsFilePath)) {
            fs.copyToLocalFile(hdfsFilePath, localDownloadPath);
            System.out.println("文件下载成功: " + localDownloadPath);
        } else {
            System.out.println("文件不存在: " + hdfsFilePath);
        }
    }
    // 查看文件元数据信息
    @Test
    public void testListFileMetadata() throws IOException {
        Path dirPath = new Path("/");
        FileStatus[] fileStatuses = fs.listStatus(dirPath);
        System.out.println("根目录下所有文件的元数据信息:");
        for (FileStatus fileStatus : fileStatuses) {
            System.out.println("文件名: " + fileStatus.getPath().getName());
            System.out.println("文件大小: " + fileStatus.getLen());
            System.out.println("文件权限: " + fileStatus.getPermission());
            System.out.println("数据块大小: " + fileStatus.getBlockSize());
            System.out.println("-----------------------------");
        }
    }
    // 读取文件内容
    @Test
    public void testReadFileContent() throws IOException {
        Path hdfsFilePath = new Path("/Java/word.txt");
        if (fs.exists(hdfsFilePath)) {
            FSDataInputStream inputStream = fs.open(hdfsFilePath);
            BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
            String line;
            System.out.println("文件内容:");
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }
            reader.close();
            inputStream.close();
        } else {
            System.out.println("文件不存在: " + hdfsFilePath);
        }
    }
    // 向文件追加内容
    @Test
    public void testAppendToFile() throws IOException {
        Path hdfsFilePath = new Path("/Java/word.txt");
        if (fs.exists(hdfsFilePath)) {
            FSDataOutputStream outputStream = fs.append(hdfsFilePath);
            outputStream.writeUTF("你好，Hadoop！");
            outputStream.close();
            System.out.println("内容追加成功: " + hdfsFilePath);
        } else {
            System.out.println("文件不存在: " + hdfsFilePath);
        }
    }
}