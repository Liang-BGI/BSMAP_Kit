args <- commandArgs()

meth <- read.table('stdin', header = T, sep = '\t')
p <- pbinom(as.numeric(meth[,7]) - 1, as.numeric(meth[,8]), 1 - as.numeric(args[6]), lower.tail = F)
fdr_p <- p.adjust(p, 'fdr')

write.table(data.frame(meth[,1:4], sprintf('%.3f', meth[,5]), sprintf('%.2f', meth[,6]), meth[,7:10], sprintf('%.4e', p), sprintf('%.4e', fdr_p)), sep = '\t', quote = F, row.names = F, col.names = c('#1.chr', '2.pos', '3.strand', '4.context', '5.ratio', '6.eff_CT_count', '7.C_count', '8.CT_count', '9.rev_G_count', '10.rev_GA_count', '11.p-value', '12.FDR_p-value'))
